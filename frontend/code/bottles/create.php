<?php
require_once '../config/database.php';

// Vérifie si l'utilisateur est connecté
if (!isset($_COOKIE['user_token']) || !isset($_COOKIE['user_id'])) {
    header('Location: /auth/login.php');
    exit;
}

// Récupère le token et l'ID de la cave
$user_token = $_COOKIE['user_token'];
$cellar_id = $_GET['cellar_id'] ?? null;

if (!$cellar_id) {
    die("ID de la cave manquant.");
}

// Initialisation des variables
$error = null;
$success = null;
$name = '';
$vintage = date('Y');
$wine_type = '';
$region = '';
$country = 'France';
$price = 0;
$quantity = 1;
$notes = '';
$validation_errors = [];

// Traitement du formulaire
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name'] ?? '');
    $vintage = intval($_POST['vintage'] ?? 0);
    $wine_type = trim($_POST['wine_type'] ?? '');
    $region = trim($_POST['region'] ?? '');
    $country = trim($_POST['country'] ?? '');
    $price = floatval($_POST['price'] ?? 0);
    $quantity = intval($_POST['quantity'] ?? 0);
    $notes = trim($_POST['notes'] ?? '');

    // Validation des champs
    if (empty($name)) {
        $validation_errors['name'] = "Le nom est obligatoire.";
    }
    if ($vintage <= 1900 || $vintage > date('Y')) {
        $validation_errors['vintage'] = "Le millésime doit être valide.";
    }
    if (empty($wine_type)) {
        $validation_errors['wine_type'] = "Le type de vin est obligatoire.";
    }
    if (empty($region)) {
        $validation_errors['region'] = "La région est obligatoire.";
    }
    if (empty($country)) {
        $validation_errors['country'] = "Le pays est obligatoire.";
    }
    if ($price < 0) {
        $validation_errors['price'] = "Le prix doit être positif.";
    }
    if ($quantity <= 0) {
        $validation_errors['quantity'] = "La quantité doit être positive.";
    }

    if (empty($validation_errors)) {
        // Préparation des données pour l'API
        $apiUrl = $API_URL . "/cellars/{$cellar_id}/bottles";
        $data = [
            'name' => $name,
            'vintage' => $vintage,
            'wine_type' => $wine_type,
            'region' => $region,
            'country' => $country,
            'price' => $price,
            'quantity' => $quantity,
            'notes' => $notes,
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
                $success = "Bouteille créée avec succès !";
                header("Location: /cellars/view.php?id={$cellar_id}&success=" . urlencode($success));
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
    <title>Ajouter une Bouteille</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .error { color: red; }
        .success { color: green; }
        .validation-error { color: #d9534f; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px; }
        form { max-width: 600px; margin: 20px 0; }
        label { display: block; margin: 10px 0 5px; }
        input[type="text"], input[type="number"], select, textarea { width: 100%; padding: 8px; margin-bottom: 5px; box-sizing: border-box; }
        button { padding: 10px 15px; background: #0066cc; color: white; border: none; cursor: pointer; }
        button:hover { background: #0052a3; }
        .actions { margin-top: 20px; }
        .actions a { margin-right: 10px; text-decoration: none; color: #0066cc; }
    </style>
</head>
<body>
    <h1>Ajouter une Nouvelle Bouteille</h1>
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

        <label>Millésime:</label>
        <input type="number" name="vintage" value="<?= htmlspecialchars($vintage) ?>" min="1900" max="<?= date('Y') ?>" required>
        <?php if (isset($validation_errors['vintage'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['vintage']) ?></p>
        <?php endif; ?>

        <label>Type de Vin:</label>
        <select name="wine_type" required>
            <option value="">-- Sélectionnez --</option>
            <option value="Rouge" <?= $wine_type === 'Rouge' ? 'selected' : '' ?>>Rouge</option>
            <option value="Blanc" <?= $wine_type === 'Blanc' ? 'selected' : '' ?>>Blanc</option>
            <option value="Rosé" <?= $wine_type === 'Rosé' ? 'selected' : '' ?>>Rosé</option>
            <option value="Champagne" <?= $wine_type === 'Champagne' ? 'selected' : '' ?>>Champagne</option>
            <option value="Autre" <?= $wine_type === 'Autre' ? 'selected' : '' ?>>Autre</option>
        </select>
        <?php if (isset($validation_errors['wine_type'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['wine_type']) ?></p>
        <?php endif; ?>

        <label>Région:</label>
        <input type="text" name="region" value="<?= htmlspecialchars($region) ?>" required>
        <?php if (isset($validation_errors['region'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['region']) ?></p>
        <?php endif; ?>

        <label>Pays:</label>
        <input type="text" name="country" value="<?= htmlspecialchars($country) ?>" required>
        <?php if (isset($validation_errors['country'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['country']) ?></p>
        <?php endif; ?>

        <label>Prix (€):</label>
        <input type="number" name="price" step="0.01" value="<?= htmlspecialchars($price) ?>" min="0" required>
        <?php if (isset($validation_errors['price'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['price']) ?></p>
        <?php endif; ?>

        <label>Quantité:</label>
        <input type="number" name="quantity" value="<?= htmlspecialchars($quantity) ?>" min="1" required>
        <?php if (isset($validation_errors['quantity'])): ?>
            <p class="validation-error"><?= htmlspecialchars($validation_errors['quantity']) ?></p>
        <?php endif; ?>

        <label>Notes (optionnel):</label>
        <textarea name="notes" rows="3"><?= htmlspecialchars($notes) ?></textarea>

        <button type="submit">Ajouter</button>
    </form>

    <div class="actions">
        <a href="/cellars/view.php?id=<?= htmlspecialchars($cellar_id) ?>">Retour à la cave</a>
    </div>
</body>
</html>
