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
$user = null;

// Récupère les informations de l'utilisateur connecté
$apiUrl = $API_URL . "/users/{$user_id}";
$options = [
    'http' => [
        'header' => [
            "Authorization: Bearer {$user_token}",
            "Content-type: application/json\r\n",
        ],
        'method' => 'GET',
        'ignore_errors' => true,
    ],
];

$response = executeApiRequest($apiUrl, $options);

if ($response === FALSE) {
    $error = "Erreur de connexion à l'API pour récupérer vos informations.";
} else {
    $result = json_decode($response, true);
    if (json_last_error() !== JSON_ERROR_NONE || !is_array($result)) {
        $error = "Réponse API invalide.";
    } else {
        $user = $result;
    }
}

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
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Mon Compte</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            background-color: #f9f9f9;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .error {
            color: red;
            background: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .user-info {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        .user-info p {
            margin: 10px 0;
        }
        .detail-label {
            font-weight: bold;
            color: #555;
            display: inline-block;
            min-width: 120px;
        }
        .role-admin {
            color: #dc3545;
            font-weight: bold;
        }
        .role-user {
            color: #28a745;
        }
        .actions {
            margin: 20px 0;
            text-align: center;
        }
        .actions a {
            display: inline-block;
            margin: 0 10px;
            padding: 8px 15px;
            text-decoration: none;
            color: white;
            border-radius: 4px;
            font-weight: bold;
        }
        .edit-btn {
            background: #007bff;
        }
        .edit-btn:hover {
            background: #0069d9;
        }
        .back-btn {
            background: #6c757d;
        }
        .back-btn:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <h1>Mon Compte</h1>

    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <?php if ($user): ?>
        <div class="user-info">
            <p>
                <span class="detail-label">Nom:</span>
                <?= htmlspecialchars($user['name'] ?? '') ?>
            </p>
            <p>
                <span class="detail-label">Email:</span>
                <?= htmlspecialchars($user['email'] ?? '') ?>
            </p>
            <p>
                <span class="detail-label">Rôle:</span>
                <span class="<?= ($user['role'] === 'admin') ? 'role-admin' : 'role-user' ?>">
                    <?= htmlspecialchars(ucfirst($user['role'] ?? '')) ?>
                </span>
            </p>
            <p>
                <span class="detail-label">Date d'inscription:</span>
                <?= htmlspecialchars(date('d/m/Y H:i', strtotime($user['created_at'] ?? ''))) ?>
            </p>
        </div>

        <div class="actions">
            <a href="/users/edit.php?id=<?= htmlspecialchars($user['id']) ?>" class="edit-btn">Modifier mes informations</a>
            <a href="/cellars/index.php" class="back-btn">Retour à mes caves</a>
        </div>
    <?php else: ?>
        <p>Impossible de récupérer vos informations.</p>
        <div class="actions">
            <a href="/cellars/index.php" class="back-btn">Retour à mes caves</a>
        </div>
    <?php endif; ?>
</body>
</html>
