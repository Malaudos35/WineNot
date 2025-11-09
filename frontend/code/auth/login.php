<?php
// session_start();
require_once '../config/database.php';

$error = null;
$email = $_POST['email'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $apiUrl = $API_URL . "/tokens";
    $data = json_encode(['email' => $email, 'password' => $password]);

    $options = [
        'http' => [
            'header' => "Content-type: application/json\r\n",
            'method' => 'POST',
            'content' => $data,
            'ignore_errors' => true,
        ],
    ];

    $context = stream_context_create($options);
    $response = @file_get_contents($apiUrl, false, $context);

    if ($response === FALSE) {
        $error = "Erreur de connexion à l'API. Veuillez réessayer plus tard.";
    } else {
        $result = json_decode($response, true);
        if (isset($result['token'])) {
            // Stocke le token et user_id dans les cookies (valable 1h)
            setcookie('user_token', $result['token'], time() + 3600, '/', '', true, true);
            setcookie('user_id', $result['user_id'], time() + 3600, '/', '', true, true);

            header('Location: /cellars/index.php');
            exit;
        } else {
            $error = $result['message'] ?? "Email ou mot de passe incorrect.";
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Connexion</title>
</head>
<body>
    <h1>Connexion</h1>
    <?php if ($error): ?>
        <p style="color: red;"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>
    <form method="POST">
        <label>Email:</label>
        <input type="email" name="email" value="<?= htmlspecialchars($email) ?>" required><br>
        <label>Mot de passe:</label>
        <input type="password" name="password" required><br>
        <button type="submit">Se connecter</button>
    </form>
    <p>Pas de compte ? <a href="/auth/register.php">S'inscrire</a></p>
</body>
</html>
