<?php
require_once '../config/database.php';

$error = null;
$success = null;
$email = $_POST['email'] ?? '';
$username = $_POST['username'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    // Validation des champs
    if (empty($email) || empty($username) || empty($password)) {
        $error = "Tous les champs sont obligatoires.";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = "L'email n'est pas valide.";
    } else {
        $apiUrl = $API_URL . "/users";
        $data = json_encode([
            'email' => $email,
            'username' => $username,
            'password' => $password
        ]);

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
            if (isset($result['id'])) {
                $success = "Compte créé avec succès ! Vous pouvez maintenant vous connecter.";
            } else {
                $error = $result['message'] ?? "Erreur lors de la création du compte.";
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Inscription</title>
</head>
<body>
    <h1>Inscription</h1>
    <?php if ($error): ?>
        <p style="color: red;"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>
    <?php if ($success): ?>
        <p style="color: green;"><?= htmlspecialchars($success) ?></p>
        <p><a href="/auth/login.php">Se connecter</a></p>
    <?php else: ?>
        <form method="POST">
            <label>Email:</label>
            <input type="email" name="email" value="<?= htmlspecialchars($email) ?>" required><br>
            <label>Nom d'utilisateur:</label>
            <input type="text" name="username" value="<?= htmlspecialchars($username) ?>" required><br>
            <label>Mot de passe:</label>
            <input type="password" name="password" required><br>
            <button type="submit">S'inscrire</button>
        </form>
        <p>Déjà un compte ? <a href="/auth/login.php">Se connecter</a></p>
    <?php endif; ?>
</body>
</html>
