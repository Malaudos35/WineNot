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

// Initialisation des variables
$error = null;
$success = null;
$cellar_name = "";

// 1. Récupère le nom de la cave pour la confirmation
$apiUrl = $API_URL . "/cellars/{$cellar_id}";
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
        $cellar_name = $result['name'];
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

        if ($http_code == 204) {
            $success = "Cave supprimée avec succès !";
            header("Location: /cellars/index.php?success=" . urlencode($success));
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
    <title>Supprimer la Cave</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .error { color: red; }
        .success { color: green; }
        .confirmation { background: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .actions { margin-top: 20px; }
        .actions a { margin-right: 10px; text-decoration: none; color: #0066cc; }
        button {
            padding: 10px 15px;
            margin-right: 10px;
            cursor: pointer;
        }
        .delete-btn { background: #d9534f; color: white; border: none; }
        .delete-btn:hover { background: #c9302c; }
        .cancel-btn { background: #f0ad4e; color: white; border: none; }
        .cancel-btn:hover { background: #ec971f; }
    </style>
</head>
<body>
    <h1>Supprimer la Cave</h1>
    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <div class="confirmation">
        <?php if ($cellar_name): ?>
            <p>Êtes-vous sûr de vouloir supprimer la cave "<strong><?= htmlspecialchars($cellar_name) ?></strong>" ?</p>
            <p>Cette action est irréversible.</p>
        <?php else: ?>
            <p>Êtes-vous sûr de vouloir supprimer cette cave ?</p>
        <?php endif; ?>

        <form method="POST">
            <button type="submit" class="delete-btn">Supprimer</button>
            <a href="/cellars/index.php" class="cancel-btn">Annuler</a>
        </form>
    </div>
</body>
</html>
