<?php
// Supprime les cookies
setcookie('user_token', '', time() - 3600, '/', '', true, true);
setcookie('user_id', '', time() - 3600, '/', '', true, true);

// Redirige vers la page de connexion
header('Location: /auth/login.php');
exit;
?>
