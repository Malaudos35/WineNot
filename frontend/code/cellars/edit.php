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
$cellar = [];
$validation_errors = [];

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
} else {
    $result = json_decode($response, true);
    if (isset($result['error'])) {
        $error = $result['message'] ?? "Erreur inconnue.";
    } else {
        $cellar = $result;
    }
}

// 2. Traitement du formulaire de modification
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name'] ?? '');
    $location = trim($_POST['location'] ?? '');
    $capacity = intval($_POST['capacity'] ?? 0);

    // Préparation des données pour l'API
    $updateData = [
        'name' => $name,
        'location' => $location,
        'capacity' => $capacity,
    ];

    // Envoi de la requête PUT
    $updateOptions = [
        'http' => [
            'header' => [
                "Authorization: Bearer {$user_token}",
                "Content-Type: application/json",
            ],
            'method' => 'PUT',
            'content' => json_encode($updateData),
            'ignore_errors' => true,
        ],
    ];

    $updateContext = stream_context_create($updateOptions);
    $updateResponse = @file_get_contents($apiUrl, false, $updateContext);

    if ($updateResponse === FALSE) {
        $error = "Erreur lors de la mise à jour. Veuillez réessayer.";
    } else {
        $http_code = null;
        if (isset($http_response_header)) {
            $http_code = explode(' ', $http_response_header[0])[1];
        }

        $updateResult = json_decode($updateResponse, true);

        if ($http_code == 200 && isset($updateResult['id'])) {
            $success = "Cave mise à jour avec succès !";
            $cellar = $updateResult; // Met à jour les données affichées
        } else {
            // Affiche les erreurs de validation ou le message d'erreur
            if (isset($updateResult['detail'])) {
                $validation_errors = $updateResult['detail'];
            } elseif (isset($updateResult['message'])) {
                $error = $updateResult['message'];
            } else {
                $error = "Erreur inconnue lors de la mise à jour (Code HTTP: " . ($http_code ?? 'inconnu') . ").";
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Modifier la Cave</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .error { color: red; }
        .success { color: green; }
        .validation-error { color: #d9534f; font-size: 0.9em; }
        form { max-width: 500px; margin: 20px 0; }
        label { display: block; margin: 10px 0 5px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 8px; margin-bottom: 5px; }
        button { padding: 10px 15px; background: #0066cc; color: white; border: none; cursor: pointer; }
        button:hover { background: #0052a3; }
        .actions { margin-top: 20px; }
        .actions a { margin-right: 10px; text-decoration: none; color: #0066cc; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Modifier la Cave</h1>
    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>
    <?php if ($success): ?>
        <p class="success"><?= htmlspecialchars($success) ?></p>
    <?php endif; ?>

    <!-- Debug: Affiche les données envoyées et la réponse (à supprimer en production) -->
    <!-- < ?php if ($_SERVER['REQUEST_METHOD'] === 'POST'): ?>
        <pre>Données envoyées : < ?= htmlspecialchars(json_encode($updateData, JSON_PRETTY_PRINT)) ?></pre>
        < ?php if (isset($updateResponse)): ?>
            <pre>Réponse API : < ?= htmlspecialchars($updateResponse) ?></pre>
        < ?php endif; ?>
    < ?php endif; ?> -->

    <?php if ($cellar): ?>
        <form method="POST">
            <label>Nom:</label>
            <input type="text" name="name" value="<?= htmlspecialchars($cellar['name'] ?? '') ?>" required>
            <?php if (isset($validation_errors['name'])): ?>
                <p class="validation-error"><?= htmlspecialchars($validation_errors['name'][0] ?? '') ?></p>
            <?php endif; ?>

            <label>Emplacement:</label>
            <input type="text" name="location" value="<?= htmlspecialchars($cellar['location'] ?? '') ?>" required>
            <?php if (isset($validation_errors['location'])): ?>
                <p class="validation-error"><?= htmlspecialchars($validation_errors['location'][0] ?? '') ?></p>
            <?php endif; ?>

            <label>Capacité:</label>
            <input type="number" name="capacity" value="<?= htmlspecialchars($cellar['capacity'] ?? 0) ?>" min="1" required>
            <?php if (isset($validation_errors['capacity'])): ?>
                <p class="validation-error"><?= htmlspecialchars($validation_errors['capacity'][0] ?? '') ?></p>
            <?php endif; ?>

            <button type="submit">Enregistrer</button>
        </form>

        <div class="actions">
            <a href="/cellars/view.php?id=<?= htmlspecialchars($cellar['id']) ?>">Retour aux détails</a>
            <a href="/cellars/index.php">Retour à la liste</a>
        </div>
    <?php else: ?>
        <p class="error">Cave non trouvée.</p>
        <a href="/cellars/index.php">Retour à la liste</a>
    <?php endif; ?>
</body>
</html>
