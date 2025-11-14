<?php
// Vérifie si l'utilisateur est connecté
$is_logged_in = isset($_COOKIE['user_token']) && isset($_COOKIE['user_id']);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestion de Cave à Vin</title>
    <style>
        /* Reset et base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
        }
        a {
            text-decoration: none;
            color: #0066cc;
        }
        a:hover {
            text-decoration: underline;
        }

        /* En-tête */
        header {
            background: #2c3e50;
            color: white;
            padding: 1rem 0;
            text-align: center;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        /* Navigation */
        nav {
            background: #34495e;
            padding: 0.5rem 0;
        }
        nav ul {
            display: flex;
            justify-content: center;
            list-style: none;
            gap: 1.5rem;
        }
        nav a {
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background 0.3s;
        }
        nav a:hover {
            background: #2c3e50;
            text-decoration: none;
        }

        /* Contenu principal */
        main {
            padding: 2rem 0;
        }
        .hero {
            text-align: center;
            padding: 2rem 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .feature {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .feature h3 {
            margin-bottom: 1rem;
            color: #2c3e50;
        }

        /* Pied de page */
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 1rem 0;
            margin-top: 2rem;
        }

        /* Boutons */
        .btn {
            display: inline-block;
            padding: 0.7rem 1.5rem;
            background: #0066cc;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            margin: 0.5rem;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0052a3;
        }
        .btn-secondary {
            background: #5bc0de;
        }
        .btn-secondary:hover {
            background: #31b0d5;
        }

        /* Responsive */
        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }
            nav ul {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Gestion de Cave à Vin</h1>
            <p class="subtitle">Organisez et gérez votre collection de vins en ligne</p>
        </div>
    </header>

    <nav>
        <div class="container">
            <ul>
                <?php if ($is_logged_in): ?>
                    <li><a href="/cellars/index.php">Mes Caves</a></li>
                    <li><a href="/auth/logout.php">Déconnexion</a></li>
                <?php else: ?>
                    <li><a href="/auth/login.php">Connexion</a></li>
                    <li><a href="/auth/register.php">Inscription</a></li>
                <?php endif; ?>
            </ul>
        </div>
    </nav>

    <main class="container">
        <section class="hero">
            <h2>Bienvenue sur votre gestionnaire de cave à vin</h2>
            <p>Gérez votre collection de vins en toute simplicité. Ajoutez, modifiez et organisez vos bouteilles et caves en ligne.</p>
            <?php if (!$is_logged_in): ?>
                <a href="/auth/register.php" class="btn">Créer un compte</a>
                <a href="/auth/login.php" class="btn btn-secondary">Se connecter</a>
            <?php else: ?>
                <a href="/cellars/index.php" class="btn">Voir mes caves</a>
            <?php endif; ?>
        </section>

        <section>
            <h2>Fonctionnalités</h2>
            <div class="features">
                <div class="feature">
                    <h3>Gestion des Caves</h3>
                    <p>Créez et organisez vos caves à vin. Ajoutez des emplacements et suivez leur capacité.</p>
                </div>
                <div class="feature">
                    <h3>Catalogue de Bouteilles</h3>
                    <p>Ajoutez et gérez vos bouteilles avec leurs détails : millésime, région, prix, notes, etc.</p>
                </div>
                <div class="feature">
                    <h3>Suivi et Recherche</h3>
                    <p>Trouvez facilement vos bouteilles grâce à des filtres et un système de recherche avancé.</p>
                </div>
            </div>
        </section>

        <?php if ($is_logged_in): ?>
            <section>
                <h2>Accès Rapide</h2>
                <div class="features">
                    <div class="feature">
                        <h3><a href="/cellars/index.php">Mes Caves</a></h3>
                        <p>Voir et gérer toutes vos caves à vin.</p>
                    </div>
                    <div class="feature">
                        <h3><a href="/cellars/create.php">Ajouter une Cave</a></h3>
                        <p>Créez une nouvelle cave pour organiser vos bouteilles.</p>
                    </div>
                </div>
            </section>
        <?php endif; ?>
    </main>

    <footer>
        <div class="container">
            <p>&copy; <?= date('Y') ?> Gestion de Cave à Vin. Tous droits réservés.</p>
        </div>
    </footer>
</body>
</html>
