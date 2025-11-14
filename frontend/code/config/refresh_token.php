<?php
// /config/refresh_token.php
function refreshAccessToken() {
    if (!isset($_COOKIE['user_token'])) {
        return false; // Pas de token disponible
    }

    $user_token = $_COOKIE['user_token'];
    $apiUrl = $GLOBALS['API_URL'] . "/refresh";

    $options = [
        'http' => [
            'header' => [
                "Authorization: Bearer {$user_token}",
                "Content-type: application/json\r\n",
            ],
            'method' => 'POST',
            'ignore_errors' => true,
        ],
    ];

    $context = stream_context_create($options);
    $response = @file_get_contents($apiUrl, false, $context);

    if ($response === FALSE) {
        return false; // Erreur de connexion
    }

    $result = json_decode($response, true);
    if (isset($result['token'])) {
        // Met à jour le token avec le nouveau token rafraîchi
        setcookie('user_token', $result['token'], time() + 3600, '/', '', true, true);
        return true;
    }

    return false; // Échec du rafraîchissement
}
?>
