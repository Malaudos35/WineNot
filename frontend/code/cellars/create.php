<?php
require_once '../config/database.php';

// Vérifie si l'utilisateur est connecté
if (!isset($_COOKIE['user_token']) || !isset($_COOKIE['user_id'])) {
    header('Location: /auth/login.php');
    exit;
}

// Récupère le token de l'utilisateur
$user_token = $_COOKIE['user_token'];

// Initialisation des variables
$error = null;
$success = null;
$name = '';
$location = '';
$capacity = 100; // Valeur par défaut
$validation_errors = [];

// Traitement du formulaire
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name'] ?? '');
    $location = trim($_POST['location'] ?? '');
    $capacity = intval($_POST['capacity'] ?? 0);

    // Validation des champs
    if (empty($name)) {
        $validation_errors['name'] = "Le nom est obligatoire.";
    }
    if (empty($location)) {
        $validation_errors['location'] = "L'emplacement est obligatoire.";
    }
    if ($capacity <= 0) {
        $validation_errors['capacity'] = "La capacité doit être un nombre positif.";
    }

    if (empty($validation_errors)) {
        // Préparation des données pour l'API
        $apiUrl = $API_URL . "/cellars";
        $data = [
            'name' => $name,
            'location' => $location,
            'capacity' => $capacity,
        ];

        $options = [
            'http' => [
                'header' => [
                    "Authorization: Bearer {$user_token}",
                    "Content-Type: application/json",
                ],
                'method' => 'POST',
                'content' => json_encode($data),
                'ignore_errors' => true,
            ],
        ];

        $context = stream_context_create($options);
        $response = @file_get_contents($apiUrl, false, $context);

        if ($response === FALSE) {
            $error = "Erreur de connexion à l'API. Veuillez réessayer plus tard.";
        } else {
            $result = json_decode($response, true);
            if (isset($result['id'])) {
                $success = "Cave créée avec succès !";
                header("Location: /cellars/index.php?success=" . urlencode($success));
                exit;
            } else {
                // Gestion des erreurs de validation retournées par l'API
                if (isset($result['detail'])) {
                    // Format FastAPI
                    foreach ($result['detail'] as $error) {
                        $field = $error['loc'][1] ?? 'unknown';
                        $validation_errors[$field] = $error['msg'];
                    }
                } elseif (isset($result['errors'])) {
                    // Format Laravel/Node.js
                    $validation_errors = $result['errors'];
                } else {
                    $error = $result['message'] ?? "Erreur inconnue lors de la création.";
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
    <title>Créer une Cave</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .error { color: red; }
        .success { color: green; }
        .validation-error { color: #d9534f; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px; }
        form { max-width: 500px; margin: 20px 0; }
        label { display: block; margin: 10px 0 5px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 8px; margin-bottom: 5px; box-sizing: border-box; }
        button { padding: 10px 15px; background: #0066cc; color: white; border: none; cursor: pointer; }
        button:hover { background: #0052a3; }
        .actions { margin-top: 20px; }
        .actions a { margin-right: 10px; text-decoration: none; color: #0066cc; }
    </style>
</head>
<body>
    <h1>Créer une Nouvelle Cave</h1>
    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>
    <?php if ($success): ?>
        <p class="success"><?= htmlspecialchars($success) ?></p>
    <?php endif; ?>

    <form method="POST">
        <label>Nom:</label>
        <input type="text" name="name" value="<?= htmlspecialchars($name) ?>" required>
        <?php if (isset($validation_errors['name'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['name']) ?></p>
        <?php endif; ?>

        <label>Emplacement:</label>
        <input type="text" name="location" value="<?= htmlspecialchars($location) ?>" required>
        <?php if (isset($validation_errors['location'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['location']) ?></p>
        <?php endif; ?>

        <label>Capacité:</label>
        <input type="number" name="capacity" value="<?= htmlspecialchars($capacity) ?>" min="1" required>
        <?php if (isset($validation_errors['capacity'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['capacity']) ?></p>
        <?php endif; ?>

        <button type="submit">Créer</button>
    </form>

    <div class="actions">
        <a href="/cellars/index.php">Retour à la liste</a>
    </div>
</body>
</html>
