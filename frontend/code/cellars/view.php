<?php
require_once '../config/database.php';

// Vérifie si l'utilisateur est connecté
if (!isset($_COOKIE['user_token']) || !isset($_COOKIE['user_id'])) {
    header('Location: /auth/login.php');
    exit;
}

// Récupère le token et l'ID de la cave
$user_token = $_COOKIE['user_token'];
$cellar_id = $_GET['id'] ?? null;

if (!$cellar_id) {
    die("ID de la cave manquant.");
}

// 1. Récupère les détails de la cave
$apiUrl = $API_URL . "/cellars/{$cellar_id}";
$options = [
    'http' => [
        'header' => [
            "Authorization: Bearer {$user_token}\r\n",
            "Content-type: application/json\r\n",
        ],
        'method' => 'GET',
        'ignore_errors' => true,
    ],
];

$context = stream_context_create($options);
$response = @file_get_contents($apiUrl, false, $context);

if ($response === FALSE) {
    $error = "Erreur de connexion à l'API.";
    $cellar = null;
} else {
    $result = json_decode($response, true);
    if (isset($result['error'])) {
        $error = $result['message'] ?? "Erreur inconnue.";
        $cellar = null;
    } else {
        $cellar = $result;
    }
}

// 2. Récupère les bouteilles de la cave
$bottles = [];
if ($cellar) {
    $bottlesApiUrl = $API_URL . "/cellars/{$cellar_id}/bottles";
    $bottlesResponse = @file_get_contents($bottlesApiUrl, false, $context);

    if ($bottlesResponse !== FALSE) {
        $bottlesResult = json_decode($bottlesResponse, true);
        if (!isset($bottlesResult['error'])) {
            $bottles = $bottlesResult ?? [];
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Détails de la Cave</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        .error { color: red; }
        .cellar-details { margin: 20px 0; background: #f9f9f9; padding: 15px; border-radius: 5px; }
        .cellar-details p { margin: 10px 0; }
        .actions { margin: 20px 0; }
        .actions a { margin-right: 10px; text-decoration: none; color: #0066cc; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .add-bottle-btn { display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Détails de la Cave</h1>
    <?php if (isset($error)): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <?php if ($cellar): ?>
        <div class="cellar-details">
            <p><strong>Nom:</strong> <?= htmlspecialchars($cellar['name'] ?? '') ?></p>
            <p><strong>Emplacement:</strong> <?= htmlspecialchars($cellar['location'] ?? '') ?></p>
            <p><strong>Capacité:</strong> <?= htmlspecialchars($cellar['capacity'] ?? '') ?></p>
            <p><strong>Créée le:</strong> <?= htmlspecialchars(date('d/m/Y H:i', strtotime($cellar['created_at'] ?? ''))) ?></p>
            <p><strong>Modifiée le:</strong> <?= htmlspecialchars(date('d/m/Y H:i', strtotime($cellar['updated_at'] ?? ''))) ?></p>
        </div>

        <div class="actions">
            <a href="/cellars/edit.php?id=<?= htmlspecialchars($cellar['id']) ?>">Modifier la cave</a>
            <a href="/cellars/index.php">Retour à la liste</a>
        </div>

        <!-- Section des bouteilles -->
        <h2>Bouteilles dans cette cave</h2>
        <a href="/bottles/create.php?cellar_id=<?= htmlspecialchars($cellar['id']) ?>" class="add-bottle-btn">Ajouter une bouteille</a>

        <?php if (empty($bottles)): ?>
            <p>Aucune bouteille dans cette cave.</p>
        <?php else: ?>
            <table>
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Millésime</th>
                        <th>Type</th>
                        <th>Région</th>
                        <th>Quantité</th>
                        <th>Prix (€)</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($bottles as $bottle): ?>
                        <tr>
                            <td><?= htmlspecialchars($bottle['name'] ?? '') ?></td>
                            <td><?= htmlspecialchars($bottle['vintage'] ?? '') ?></td>
                            <td><?= htmlspecialchars($bottle['wine_type'] ?? '') ?></td>
                            <td><?= htmlspecialchars($bottle['region'] ?? '') ?></td>
                            <td><?= htmlspecialchars($bottle['quantity'] ?? '') ?></td>
                            <td><?= htmlspecialchars(number_format($bottle['price'] ?? 0, 2)) ?></td>
                            <td>
                                <a href="/bottles/view.php?id=<?= htmlspecialchars($bottle['id']) ?>">Voir</a>
                                <a href="/bottles/edit.php?id=<?= htmlspecialchars($bottle['id']) ?>">Modifier</a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    <?php else: ?>
        <p>Cave non trouvée.</p>
        <a href="/cellars/index.php">Retour à la liste</a>
    <?php endif; ?>
</body>
</html>
