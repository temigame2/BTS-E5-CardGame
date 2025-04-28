import pygame
import random

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1v1 Jeu de cartes")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
GREY = (100, 100, 100)

# Types de cartes
TYPES = ["mage", "archer", "guerrier"]

# Chargement des images
#fond_image = pygame.image.load("images/fond.png")
misc_image = {
    #"fond": pygame.image.load("images/fond.png"),
    "epee": pygame.image.load("images/Epee.png"),
    "bouclier": pygame.image.load("images/Defence.png"),
    "coeur": pygame.image.load("images/Coeur.png"),
}
images_cartes = {
    "mage": pygame.image.load("images/Mage.png"),
    "archer": pygame.image.load("images/Archer.png"),
    "guerrier": pygame.image.load("images/Swordsman.png"),
}
images_objets = {
    "Pierre Magique de Force": pygame.image.load("images/Flint.png"),
    "Pierre Magique de Protection": pygame.image.load("images/Glass.png"),
    "Changement de Type": pygame.image.load("images/Combat.png"),
    "Potion": pygame.image.load("images/Wine.png"),
    "Grande Potion": pygame.image.load("images/Beer.png"),
}

# Classe pour représenter une carte
class Carte:
    def __init__(self, x, y):
        self.atk = random.randint(1, 4)
        self.defense = random.randint(0, 5)
        self.pv = random.randint(12, 25)
        self.type = random.choice(TYPES)
        self.rect = pygame.Rect(x, y, 150, 200)

        # Sauvegarde des valeurs originales
        self.atk_original = self.atk
        self.defense_original = self.defense

        # Système de niveau
        self.niveau = 1
        self.xp = 0
        self.xp_max = 0 + 1 * self.niveau  # XP nécessaire pour monter de niveau

    def draw(self, screen, scale=1.0):
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_image = pygame.transform.scale(images_cartes[self.type], (scaled_width, scaled_height))
        screen.blit(scaled_image, (self.rect.x, self.rect.y))
        scale_pv_image = pygame.transform.scale(misc_image["coeur"], (int(30 * scale), int(30 * scale)))
        screen.blit(scale_pv_image, (self.rect.x + scaled_width - 42, self.rect.y + 45))
        scale_atk_image = pygame.transform.scale(misc_image["epee"], (int(30 * scale), int(30 * scale)))
        screen.blit(scale_atk_image, (self.rect.x + 5, self.rect.y + scaled_height - 40))
        scale_def_image = pygame.transform.scale(misc_image["bouclier"], (int(30 * scale), int(30 * scale)))
        screen.blit(scale_def_image, (self.rect.x + scaled_width - 37, self.rect.y + scaled_height - 40))

        # Afficher les stats par-dessus l'image
        font = pygame.font.Font(None, int(32 * scale))
        pv_text = font.render(f"{self.pv}", True, GREY)
        screen.blit(pv_text, (self.rect.x + scaled_width - pv_text.get_width() - 15, self.rect.y + 50))
        atk_text = font.render(f"{self.atk}", True, GREY)
        screen.blit(atk_text, (self.rect.x + 15, self.rect.y + scaled_height - atk_text.get_height() - 15))
        def_text = font.render(f"{self.defense}", True, GREY)
        screen.blit(def_text, (self.rect.x + scaled_width - def_text.get_width() - 15, self.rect.y + scaled_height - def_text.get_height() - 15))

    def reset_stats(self):
        self.atk = self.atk_original
        self.defense = self.defense_original

    def gagner_xp(self, xp_gagne):
        self.xp += xp_gagne
        if self.xp >= self.xp_max:
            self.xp -= self.xp_max
            self.niveau += 1
            self.xp_max += 2  # Augmente la difficulté pour le prochain niveau

            # Appeler le menu de choix de stat
            afficher_menu_level_up(self)

    def augmenter_stat(self):
        choix = random.choice(["atk", "defense", "pv"])
        if choix == "atk":
            self.atk += 1
            self.atk_original += 1
        elif choix == "defense":
            self.defense += 1
            self.defense_original += 1
        elif choix == "pv":
            self.pv += 5  # Augmente les PV de manière significative


# Classe pour représenter un projectile
class Projectile:
    def __init__(self, x, y, cible_x, cible_y):
        self.x = x
        self.y = y
        self.cible_x = cible_x
        self.cible_y = cible_y
        self.vitesse = 3
        self.rect = pygame.Rect(x, y, 30, 30)

    def move(self):
        dx = self.cible_x - self.x
        dy = self.cible_y - self.y
        distance = (dx**2 + dy**2)**0.5
        if distance != 0:
            dx /= distance
            dy /= distance

        self.x += dx * self.vitesse
        self.y += dy * self.vitesse
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.ellipse(screen, RED, self.rect)

    def atteint_cible(self):
        return self.rect.collidepoint(self.cible_x, self.cible_y)

# Classe pour représenter une carte objet
class CarteObjet:
    def __init__(self, x, y, nom, effet):
        self.nom = nom
        self.effet = effet
        self.rect = pygame.Rect(x, y, 100, 150)
        self.image = images_objets[nom]  # Associe l'image à l'objet

    def draw(self, screen):
        # Redimensionne l'image pour s'adapter au rectangle
        scaled_image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        screen.blit(scaled_image, (self.rect.x, self.rect.y))

# Fonction pour calculer les dégâts
def calculer_degats(carte1, carte2):
    avantages = {"mage": "guerrier", "guerrier": "archer", "archer": "mage"}
    bonus = 2 if avantages[carte1.type] == carte2.type else 0
    return max(1, carte1.atk + bonus - carte2.defense)

# Fonction pour afficher un menu
def afficher_menu(message, bouton_message):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    text = font.render(message, True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    bouton = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, GREEN, bouton)
    bouton_text = font.render(bouton_message, True, WHITE)
    screen.blit(bouton_text, (bouton.x + 5, bouton.y + 10))
    pygame.display.flip()
    return bouton

# Fonction pour afficher un menu avec des objets à choisir
def afficher_menu_objets(message, objets_disponibles, main_joueur):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    text = font.render(message, True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

    # Afficher les objets disponibles
    boutons_objets = []
    for i, objet in enumerate(objets_disponibles):
        bouton = pygame.Rect(50 + i * 150, HEIGHT // 2, 100, 150)
        pygame.draw.rect(screen, GREEN, bouton)
        font_objet = pygame.font.Font(None, 24)
        nom_text = font_objet.render(objet.nom, True, WHITE)
        screen.blit(nom_text, (bouton.x + 5, bouton.y + 5))
        boutons_objets.append((bouton, objet))

    pygame.display.flip()

    # Attente du choix de l'utilisateur
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for bouton, objet in boutons_objets:
                    if bouton.collidepoint(event.pos):
                        # Ajouter ou échanger l'objet
                        if len(main_joueur) < 3:
                            main_joueur.append(objet)
                        else:
                            bouton_echange = afficher_menu_echange(main_joueur)
                            for event_echange in pygame.event.get():
                                if event_echange.type == pygame.MOUSEBUTTONDOWN:
                                    for i, carte in enumerate(main_joueur):
                                        if bouton_echange[i].collidepoint(event_echange.pos):
                                            main_joueur[i] = objet
                                            break
                        attente = False
                        break

# Fonction pour afficher un menu d'échange
def afficher_menu_echange(main_joueur):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)
    text = font.render("Choisissez un objet à échanger", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

    boutons_main = []
    for i, carte in enumerate(main_joueur):
        bouton = pygame.Rect(50 + i * 150, HEIGHT // 2, 100, 150)
        pygame.draw.rect(screen, RED, bouton)
        font_carte = pygame.font.Font(None, 24)
        nom_text = font_carte.render(carte.nom, True, WHITE)
        screen.blit(nom_text, (bouton.x + 5, bouton.y + 5))
        boutons_main.append(bouton)

    pygame.display.flip()
    return boutons_main

def afficher_menu_level_up(carte):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    text = font.render("Choisissez une stat à augmenter :", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

    # Boutons pour les stats
    boutons_stats = {
        "atk": pygame.Rect(WIDTH // 4 - 50, HEIGHT // 2, 100, 50),
        "defense": pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 50),
        "pv": pygame.Rect(3 * WIDTH // 4 - 50, HEIGHT // 2, 100, 50),
    }

    for stat, bouton in boutons_stats.items():
        pygame.draw.rect(screen, GREEN, bouton)
        stat_text = font.render(stat, True, WHITE)
        screen.blit(stat_text, (bouton.x + 10, bouton.y + 10))

    pygame.display.flip()

    # Attente du choix de l'utilisateur
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for stat, bouton in boutons_stats.items():
                    if bouton.collidepoint(event.pos):
                        if stat == "atk":
                            carte.atk += 1
                            carte.atk_original += 1
                        elif stat == "defense":
                            carte.defense += 1
                            carte.defense_original += 1
                        elif stat == "pv":
                            carte.pv += 5
                        attente = False
                        break

# Fonction pour gérer l'animation de combat
def animation_combat(carte1, carte2):
    for _ in range(3):
        pygame.draw.rect(screen, RED, carte1.rect, 5)
        pygame.draw.rect(screen, RED, carte2.rect, 5)
        pygame.display.flip()
        pygame.time.wait(200)
        screen.fill(WHITE)
        carte1.draw(screen)
        carte2.draw(screen)
        pygame.display.flip()
        pygame.time.wait(200)

def reordonner_main(main_joueur):
    for i, carte in enumerate(main_joueur):
        carte.rect.x = 50 + i * 120  # Position horizontale avec un espacement de 120 pixels
        carte.rect.y = 425          # Position verticale fixe

# Création des cartes des deux joueurs
carte_joueur1 = Carte(100, 200)
carte_joueur2 = Carte(550, 200)

# Liste des cartes objet disponibles
cartes_objet_disponibles = [
    ("Potion", lambda joueur: setattr(joueur, "pv", joueur.pv + 10)),
    ("Grande Potion", lambda joueur: setattr(joueur, "pv", joueur.pv + 20)),
    ("Changement de Type", lambda joueur: setattr(joueur, "type", random.choice([t for t in TYPES if t != joueur.type]))),
    ("Pierre Magique de Force", lambda joueur: setattr(joueur, "atk", joueur.atk * 2)),
    ("Pierre Magique de Protection", lambda joueur: setattr(joueur, "defense", joueur.defense + 9999)),
]

# Création de la main avec des cartes objet
main_joueur1 = [
    CarteObjet(50 + i * 120, 425, *random.choice(cartes_objet_disponibles)) for i in range(3)
]

# Menu de début
bouton_start = afficher_menu("Bienvenue dans le jeu de cartes 1v1", "Commencer")
attente = True
while attente:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and bouton_start.collidepoint(event.pos):
            attente = False

# Variable pour suivre le tour (1 pour joueur 1, 2 pour joueur 2)
tour_joueur = 1
# Liste pour stocker les projectiles actifs
projectiles = []
# Initialisation du nombre d'étages
nombre_etages = 1

# Boucle principale mise à jour
running = True
while running:
    screen.fill(WHITE)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifier si une carte objet est cliquée
            for carte in main_joueur1:
                if carte.rect.collidepoint(event.pos):
                    carte.effet(carte_joueur1)
                    main_joueur1.remove(carte)
                    break
            # Vérifier si l'ennemi est cliqué pour attaquer
            if tour_joueur == 1 and carte_joueur1.pv > 0 and carte_joueur2.pv > 0:
                if carte_joueur2.rect.collidepoint(event.pos):  # Si clic sur l'ennemi
                    projectile = Projectile(carte_joueur1.rect.centerx, carte_joueur1.rect.centery,
                                            carte_joueur2.rect.centerx, carte_joueur2.rect.centery)
                    projectiles.append(projectile)

    # Déplacer et dessiner les projectiles
    for projectile in projectiles[:]:
        projectile.move()
        projectile.draw(screen)

        if projectile.atteint_cible():
            if tour_joueur == 1:
                degats = calculer_degats(carte_joueur1, carte_joueur2)
                carte_joueur2.pv -= degats
                tour_joueur = 2  # Passer au tour de l'ennemi
            elif tour_joueur == 2:
                degats = calculer_degats(carte_joueur2, carte_joueur1)
                carte_joueur1.pv -= degats
                tour_joueur = 1  # Revenir au tour du joueur
            projectiles.remove(projectile)
            pygame.time.wait(500)  # Attente entre les attaques

    # Attaque automatique de l'ennemi
    if tour_joueur == 2 and carte_joueur2.pv > 0 and carte_joueur1.pv > 0 and not projectiles:
        projectile = Projectile(carte_joueur2.rect.centerx, carte_joueur2.rect.centery,
                                carte_joueur1.rect.centerx, carte_joueur1.rect.centery)
        projectiles.append(projectile)

    # À la fin du tour du joueur
    if tour_joueur == 2:  # Passer au tour de l'ennemi
        carte_joueur1.reset_stats()
    elif tour_joueur == 1:  # Revenir au tour du joueur
        carte_joueur2.reset_stats()

    # Dessiner les cartes
    carte_joueur1.draw(screen)
    carte_joueur2.draw(screen)

    # Dessiner les cartes de la main du joueur 1
    for carte in main_joueur1:
        carte.draw(screen)

    # Affichage du niveau et de l'XP
    font = pygame.font.Font(None, 36)
    niveau_text = font.render(f"Niveau: {carte_joueur1.niveau} | XP: {carte_joueur1.xp}/{carte_joueur1.xp_max}", True, BLACK)
    screen.blit(niveau_text, (10, 10))

    # Affichage du nombre d'étages en haut à droite
    font = pygame.font.Font(None, 36)
    etages_text = font.render(f"Étage: {nombre_etages}", True, BLACK)
    screen.blit(etages_text, (WIDTH - etages_text.get_width() - 10, 10))

    # Vérification des PV
    font = pygame.font.Font(None, 36)
    if carte_joueur1.pv <= 0 or carte_joueur2.pv <= 0:
        if carte_joueur1.pv <= 0:  # Si le joueur 2 gagne
            # Afficher le menu de Game Over
            bouton_game_over = afficher_menu("Game Over - Joueur 2 a gagné !", "Quitter")
            attente = True
            while attente:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and bouton_game_over.collidepoint(event.pos):
                        pygame.quit()
                        exit()

        gagnant = "Joueur 1" if carte_joueur2.pv <= 0 else "Joueur 2"

        # Générer des objets aléatoires si le joueur 1 gagne
        if gagnant == "Joueur 1":
            nombre_etages += 1  # Incrémente le nombre d'étages
            objets_disponibles = [
                CarteObjet(0, 0, *random.choice(cartes_objet_disponibles)) for _ in range(random.randint(2, 5))
            ]

            # Afficher le menu des objets
            afficher_menu_objets(f"{gagnant} a gagné ! Choisissez un objet :", objets_disponibles, main_joueur1)

            carte_joueur1.gagner_xp(1)

            # Afficher un message pour continuer
            bouton_fin = afficher_menu("Continuer ?", "Continuer")
            attente = True
            while attente:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and bouton_fin.collidepoint(event.pos):
                        # Ne réinitialise pas les cartes ou la main
                        carte_joueur1.reset_stats()
                        carte_joueur2 = Carte(550, 200)  # Génère une nouvelle carte pour l'adversaire
                        tour_joueur = 1
                        attente = False

    # Mise à jour de l'affichage
    pygame.display.flip()

# Quitter pygame
pygame.quit()