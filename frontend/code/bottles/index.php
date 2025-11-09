<?php
require_once '../config/database.php';
require_once '../config/refresh_token.php';

// Vérifie si l'utilisateur est connecté
if (!isset($_COOKIE['user_token']) || !isset($_COOKIE['user_id'])) {
    header('Location: /auth/login.php');
    exit;
}

$user_token = $_COOKIE['user_token'];
$user_id = $_COOKIE['user_id'];
$error = null;
$grouped_bottles = [];
$cellar_names = []; // Tableau pour mapper les IDs des caves à leurs noms

// Fonction pour exécuter une requête API avec rafraîchissement automatique
function executeApiRequest($url, $options) {
    $context = stream_context_create($options);
    $response = @file_get_contents($url, false, $context);

    if ($response === FALSE) {
        return false;
    }

    $http_code = null;
    if (isset($GLOBALS['http_response_header'])) {
        $http_code = explode(' ', $GLOBALS['http_response_header'][0])[1];
    }

    if ($http_code == 401) {
        if (refreshAccessToken()) {
            $new_token = $_COOKIE['user_token'];
            $options['http']['header'] = [
                "Authorization: Bearer {$new_token}",
                "Content-type: application/json\r\n",
            ];
            $context = stream_context_create($options);
            $response = @file_get_contents($url, false, $context);
        } else {
            setcookie('user_token', '', time() - 3600, '/');
            header('Location: /auth/login.php?error=session_expired');
            exit;
        }
    }

    return $response;
}

// 1. Récupère la liste des caves de l'utilisateur
$cellars_api_url = $API_URL . "/cellars";
$cellars_options = [
    'http' => [
        'header' => [
            "Authorization: Bearer {$user_token}",
            "Content-type: application/json\r\n",
        ],
        'method' => 'GET',
        'ignore_errors' => true,
    ],
];

$cellars_response = executeApiRequest($cellars_api_url, $cellars_options);

if ($cellars_response === FALSE) {
    $error = "Erreur de connexion à l'API pour récupérer les caves.";
} else {
    $cellars_result = json_decode($cellars_response, true);
    if (json_last_error() !== JSON_ERROR_NONE || !is_array($cellars_result)) {
        $error = "Réponse API invalide pour les caves.";
    } else {
        $cellars = $cellars_result;
        // Crée un tableau associatif pour mapper les IDs des caves à leurs noms
        foreach ($cellars as $cellar) {
            if (isset($cellar['id']) && isset($cellar['name'])) {
                $cellar_names[$cellar['id']] = $cellar['name'];
            }
        }
    }
}

// 2. Pour chaque cave, récupère les bouteilles
if (!empty($cellars) && is_array($cellars)) {
    foreach ($cellars as $cellar) {
        $cellar_id = $cellar['id'] ?? '';
        if (empty($cellar_id)) continue;

        $bottles_api_url = $API_URL . "/cellars/{$cellar_id}/bottles";
        $bottles_options = [
            'http' => [
                'header' => [
                    "Authorization: Bearer {$user_token}",
                    "Content-type: application/json\r\n",
                ],
                'method' => 'GET',
                'ignore_errors' => true,
            ],
        ];

        $bottles_response = executeApiRequest($bottles_api_url, $bottles_options);

        if ($bottles_response !== FALSE) {
            $bottles_result = json_decode($bottles_response, true);
            if (json_last_error() === JSON_ERROR_NONE && is_array($bottles_result)) {
                foreach ($bottles_result as $bottle) {
                    if (!is_array($bottle)) continue;

                    // Crée une clé unique pour chaque bouteille
                    $key = md5(
                        ($bottle['name'] ?? '') .
                        ($bottle['vintage'] ?? '') .
                        ($bottle['wine_type'] ?? '') .
                        ($bottle['region'] ?? '') .
                        ($bottle['country'] ?? '')
                    );

                    if (!isset($grouped_bottles[$key])) {
                        // Première occurrence de cette bouteille
                        $grouped_bottles[$key] = [
                            'id' => $bottle['id'] ?? '',
                            'name' => $bottle['name'] ?? '',
                            'vintage' => $bottle['vintage'] ?? '',
                            'wine_type' => $bottle['wine_type'] ?? '',
                            'region' => $bottle['region'] ?? '',
                            'country' => $bottle['country'] ?? '',
                            'price' => floatval($bottle['price'] ?? 0),
                            'quantity' => intval($bottle['quantity'] ?? 0),
                            'notes' => $bottle['notes'] ?? '',
                            'cellar_ids' => [$cellar_id],
                        ];
                    } else {
                        // Bouteille déjà présente, ajoute la quantité et l'ID de la cave
                        $grouped_bottles[$key]['quantity'] += intval($bottle['quantity'] ?? 0);
                        if (!in_array($cellar_id, $grouped_bottles[$key]['cellar_ids'])) {
                            $grouped_bottles[$key]['cellar_ids'][] = $cellar_id;
                        }
                    }
                }
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Mes Bouteilles</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .error {
            color: red;
            background: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            cursor: pointer;
        }
        th:hover {
            background-color: #e6e6e6;
        }
        th.sort-asc::after {
            content: " ↑";
        }
        th.sort-desc::after {
            content: " ↓";
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .actions {
            margin: 20px 0;
        }
        .actions a {
            display: inline-block;
            margin-right: 10px;
            padding: 8px 12px;
            text-decoration: none;
            color: white;
            border-radius: 4px;
            font-weight: bold;
        }
        .add-btn {
            background: #28a745;
        }
        .add-btn:hover {
            background: #218838;
        }
        .cellar-list {
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Mes Bouteilles</h1>

    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <div class="actions">
        <a href="/bottles/create.php" class="add-btn">Ajouter une Bouteille</a>
        <a href="/cellars/index.php">Retour aux Caves</a>
    </div>

    <?php if (!empty($grouped_bottles)): ?>
        <table id="bottles-table">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Nom</th>
                    <th onclick="sortTable(1)">Millésime</th>
                    <th onclick="sortTable(2)">Type</th>
                    <th onclick="sortTable(3)">Région</th>
                    <th onclick="sortTable(4)">Pays</th>
                    <th onclick="sortTable(5)">Quantité</th>
                    <th onclick="sortTable(6)">Prix Moyen</th>
                    <th onclick="sortTable(7)">Caves</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($grouped_bottles as $bottle): ?>
                    <tr>
                        <td><?= htmlspecialchars($bottle['name']) ?></td>
                        <td><?= htmlspecialchars($bottle['vintage']) ?></td>
                        <td><?= htmlspecialchars($bottle['wine_type']) ?></td>
                        <td><?= htmlspecialchars($bottle['region']) ?></td>
                        <td><?= htmlspecialchars($bottle['country']) ?></td>
                        <td><?= htmlspecialchars($bottle['quantity']) ?></td>
                        <td><?= htmlspecialchars(number_format($bottle['price'], 2)) ?> €</td>
                        <td>
                            <div class="cellar-list">
                                <?php
                                $names = [];
                                foreach ($bottle['cellar_ids'] as $id) {
                                    $names[] = htmlspecialchars($cellar_names[$id] ?? "Cave #" . substr($id, 0, 8));
                                }
                                echo implode(', ', $names);
                                ?>
                            </div>
                        </td>
                        <td>
                            <a href="/bottles/view.php?id=<?= htmlspecialchars($bottle['id']) ?>">Voir</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

        <script>
            // Variables pour le tri
            let currentColumn = -1;
            let sortDirection = 1; // 1 = croissant, -1 = décroissant

            function sortTable(columnIndex) {
                const table = document.getElementById('bottles-table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));

                // Réinitialise les classes de tri
                const headers = table.querySelectorAll('th');
                headers.forEach(header => {
                    header.classList.remove('sort-asc', 'sort-desc');
                });

                // Si on clique sur la même colonne, inverse le sens du tri
                if (currentColumn === columnIndex) {
                    sortDirection *= -1;
                } else {
                    currentColumn = columnIndex;
                    sortDirection = 1;
                }

                // Ajoute la classe de tri à l'en-tête actuel
                headers[columnIndex].classList.add(sortDirection === 1 ? 'sort-asc' : 'sort-desc');

                // Trie les lignes
                rows.sort((rowA, rowB) => {
                    const cellA = rowA.cells[columnIndex].textContent.trim();
                    const cellB = rowB.cells[columnIndex].textContent.trim();

                    // Gestion spéciale pour les nombres (quantité, prix, millésime)
                    if (columnIndex === 5 || columnIndex === 6 || columnIndex === 1) {
                        const numA = parseFloat(cellA.replace(/[^\d.-]/g, ''));
                        const numB = parseFloat(cellB.replace(/[^\d.-]/g, ''));
                        return (numA - numB) * sortDirection;
                    }

                    // Tri alphabétique pour les autres colonnes
                    return cellA.localeCompare(cellB) * sortDirection;
                });

                // Réorganise les lignes dans le tableau
                rows.forEach(row => tbody.appendChild(row));
            }
        </script>
    <?php else: ?>
        <p>Aucune bouteille trouvée.</p>
    <?php endif; ?>
</body>
</html>
