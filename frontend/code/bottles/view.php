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
$bottle = null;

// 1. Récupère les détails de la bouteille
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

if ($response === FALSE) {
    $error = "Erreur de connexion à l'API. Veuillez réessayer plus tard.";
} else {
    $result = json_decode($response, true);
    if (isset($result['error'])) {
        $error = $result['message'] ?? "Erreur inconnue.";
    } else {
        $bottle = $result;
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Détails de la Bouteille - <?= htmlspecialchars($bottle['name'] ?? 'Inconnue') ?></title>
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
        .bottle-container {
            display: flex;
            margin: 20px 0;
            gap: 20px;
        }
        .bottle-image {
            max-width: 300px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background: #f9f9f9;
        }
        .bottle-image img {
            max-width: 100%;
            height: auto;
            display: block;
        }
        .bottle-details {
            flex: 1;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
        }
        .bottle-details p {
            margin: 10px 0;
        }
        .detail-label {
            font-weight: bold;
            color: #555;
        }
        .price {
            font-weight: bold;
            color: #2a6496;
            font-size: 1.2em;
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
        }
        .edit-btn {
            background: #0066cc;
        }
        .delete-btn {
            background: #d9534f;
        }
        .back-btn {
            background: #5bc0de;
        }
        .actions a:hover {
            opacity: 0.9;
        }
        .notes {
            background: #fff;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Détails de la Bouteille</h1>

    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <?php if ($bottle): ?>
        <div class="bottle-container">
            <?php if (!empty($bottle['image_url'])): ?>
                <div class="bottle-image">
                    <img src="<?= htmlspecialchars($bottle['image_url']) ?>" alt="<?= htmlspecialchars($bottle['name']) ?>">
                </div>
            <?php endif; ?>

            <div class="bottle-details">
                <p><span class="detail-label">Nom:</span> <?= htmlspecialchars($bottle['name'] ?? '') ?></p>
                <p><span class="detail-label">Millésime:</span> <?= htmlspecialchars($bottle['vintage'] ?? '') ?></p>
                <p><span class="detail-label">Type:</span> <?= htmlspecialchars($bottle['wine_type'] ?? '') ?></p>
                <p><span class="detail-label">Région:</span> <?= htmlspecialchars($bottle['region'] ?? '') ?></p>
                <p><span class="detail-label">Pays:</span> <?= htmlspecialchars($bottle['country'] ?? '') ?></p>
                <p><span class="detail-label">Quantité:</span> <?= htmlspecialchars($bottle['quantity'] ?? '') ?></p>
                <p><span class="detail-label">Prix:</span> <span class="price"><?= htmlspecialchars(number_format($bottle['price'] ?? 0, 2)) ?> €</span></p>

                <?php if (!empty($bottle['notes'])): ?>
                    <div class="notes">
                        <p><span class="detail-label">Notes:</span></p>
                        <p><?= nl2br(htmlspecialchars($bottle['notes'])) ?></p>
                    </div>
                <?php endif; ?>
            </div>
        </div>

        <div class="actions">
            <a href="/bottles/edit.php?id=<?= htmlspecialchars($bottle['id']) ?>" class="edit-btn">Modifier</a>
            <a href="/bottles/delete.php?id=<?= htmlspecialchars($bottle['id']) ?>" class="delete-btn" onclick="return confirm('Êtes-vous sûr de vouloir supprimer cette bouteille ?')">Supprimer</a>
            <a href="/cellars/view.php?id=<?= htmlspecialchars($bottle['cellar_id'] ?? '') ?>" class="back-btn">Retour à la cave</a>
        </div>
    <?php else: ?>
        <p class="error">Bouteille non trouvée.</p>
        <div class="actions">
            <a href="/cellars/index.php" class="back-btn">Retour à la liste des caves</a>
        </div>
    <?php endif; ?>
</body>
</html>
