<?php
require_once '../config/refresh_token.php';
require_once '../config/database.php';

// Vérifie si l'utilisateur est connecté
if (!isset($_COOKIE['user_token']) || !isset($_COOKIE['user_id'])) {
    header('Location: /auth/login.php');
    exit;
}

// Récupère le token et user_id
$user_token = $_COOKIE['user_token'];
$user_id = $_COOKIE['user_id'];

// Appelle l'API pour récupérer les caves
$apiUrl = $API_URL . "/cellars";
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
    $cellars = [];
} else {
    $result = json_decode($response, true);
    if (isset($result['error'])) {
        $error = $result['message'] ?? "Erreur inconnue.";
        $cellars = [];
    } else {
        $cellars = $result ?? [];
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Mes Caves à Vin</title>
</head>
<body>
    <h1>Mes Caves à Vin</h1>
    <?php if (isset($error)): ?>
        <p style="color: red;"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>
    <a href="/cellars/create.php">Ajouter une cave</a>
    <a href="/auth/logout.php" style="float: right;">Déconnexion</a>
    <table border="1">
        <thead>
            <tr>
                <th>Nom</th>
                <th>Emplacement</th>
                <th>Capacité</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($cellars)): ?>
                <tr>
                    <td colspan="4">Aucune cave trouvée.</td>
                </tr>
            <?php else: ?>
                <?php foreach ($cellars as $cellar): ?>
                <tr>
                    <td><?= htmlspecialchars($cellar['name'] ?? '') ?></td>
                    <td><?= htmlspecialchars($cellar['location'] ?? '') ?></td>
                    <td><?= htmlspecialchars($cellar['capacity'] ?? '') ?></td>
                    <td>
                        <a href="/cellars/view.php?id=<?= $cellar['id'] ?>">Voir</a>
                        <a href="/cellars/edit.php?id=<?= $cellar['id'] ?>">Modifier</a>
                        <a href="/cellars/delete.php?id=<?= $cellar['id'] ?>" onclick="return confirm('Supprimer ?')">Supprimer</a>
                    </td>
                </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>
</body>
</html>
