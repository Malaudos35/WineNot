<?php
require_once '../config/database.php';

// Vérifie si l'utilisateur est connecté
if (!isset($_COOKIE['user_token']) || !isset($_COOKIE['user_id'])) {
    header('Location: /auth/login.php');
    exit;
}

// Récupère le token et l'ID de la bouteille
$user_token = $_COOKIE['user_token'];
$bottle_id = $_GET['id'] ?? null;

if (!$bottle_id) {
    die("ID de la bouteille manquant.");
}

// Initialisation des variables
$error = null;
$bottle_name = "";
$cellar_id = null;

// 1. Récupère le nom de la bouteille pour la confirmation
$apiUrl = $API_URL . "/bottles/{$bottle_id}";
$options = [
    'http' => [
        'header' => [
            "Authorization: Bearer {$user_token}",
            "Content-Type: application/json",
        ],
        'method' => 'GET',
        'ignore_errors' => true,
    ],
];

$context = stream_context_create($options);
$response = @file_get_contents($apiUrl, false, $context);

if ($response !== FALSE) {
    $result = json_decode($response, true);
    if (isset($result['name'])) {
        $bottle_name = $result['name'];
    }
    if (isset($result['cellar_id'])) {
        $cellar_id = $result['cellar_id'];
    }
}

// 2. Traitement de la suppression
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $deleteOptions = [
        'http' => [
            'header' => [
                "Authorization: Bearer {$user_token}",
                "Content-Type: application/json",
            ],
            'method' => 'DELETE',
            'ignore_errors' => true,
        ],
    ];

    $deleteContext = stream_context_create($deleteOptions);
    $deleteResponse = @file_get_contents($apiUrl, false, $deleteContext);

    if ($deleteResponse === FALSE) {
        $error = "Erreur lors de la suppression. Veuillez réessayer.";
    } else {
        $http_code = null;
        if (isset($http_response_header)) {
            $http_code = explode(' ', $http_response_header[0])[1];
        }

        if ($http_code == 204 || $http_code == 200) {
            $success = "Bouteille supprimée avec succès !";
            header("Location: /cellars/view.php?id={$cellar_id}&success=" . urlencode($success));
            exit;
        } else {
            $deleteResult = json_decode($deleteResponse, true);
            $error = $deleteResult['message'] ?? "Erreur inconnue lors de la suppression.";
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Supprimer la Bouteille</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .error {
            color: red;
            background: #ffebee;
            padding: 10px;
            border-radius: 5px;
        }
        .confirmation {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .actions {
            margin: 20px 0;
        }
        .actions a, .actions button {
            display: inline-block;
            margin-right: 10px;
            padding: 8px 12px;
            text-decoration: none;
            color: white;
            border-radius: 4px;
            border: none;
            cursor: pointer;
        }
        .delete-btn {
            background: #d9534f;
        }
        .cancel-btn {
            background: #5bc0de;
        }
        .delete-btn:hover, .cancel-btn:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <h1>Supprimer la Bouteille</h1>

    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <div class="confirmation">
        <?php if ($bottle_name): ?>
            <p>Êtes-vous sûr de vouloir supprimer la bouteille "<strong><?= htmlspecialchars($bottle_name) ?></strong>" ?</p>
            <p>Cette action est irréversible.</p>
        <?php else: ?>
            <p>Êtes-vous sûr de vouloir supprimer cette bouteille ?</p>
        <?php endif; ?>

        <form method="POST" class="actions">
            <button type="submit" class="delete-btn">Supprimer</button>
            <a href="/cellars/view.php?id=<?= htmlspecialchars($cellar_id) ?>" class="cancel-btn">Annuler</a>
        </form>
    </div>
</body>
</html>
