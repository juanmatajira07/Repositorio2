import pygame
import sys
import math

# ---------------------------------------------------------
# 1. Configuración Inicial y Constantes
# ---------------------------------------------------------
pygame.init()

# Dimensiones de la pantalla
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colores (RGB)
SKY_BLUE = (135, 206, 235)
MARIO_RED = (220, 20, 60)
GROUND_GREEN = (34, 139, 34)
COIN_GOLD = (255, 215, 0)
TEXT_BLACK = (0, 0, 0)
ALIEN_GREEN = (50, 205, 50)
LASER_RED = (255, 69, 0)

# Configuración de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Mario Clásico")
clock = pygame.time.Clock()

# ---------------------------------------------------------
# 2. Clases del Juego
# ---------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40) # Tamaño del jugador (ancho, alto)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -12
        self.gravity = 0.6
        self.on_ground = False

    def move(self, dx, dy, platforms):
        # Mover en el eje X
        self.rect.x += dx
        self.check_collision(dx, 0, platforms)
        
        # Mover en el eje Y (Gravedad y Saltos)
        self.rect.y += dy
        self.check_collision(0, dy, platforms)

    def check_collision(self, dx, dy, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Colisión horizontal
                if dx > 0: # Moviéndose a la derecha
                    self.rect.right = platform.rect.left
                if dx < 0: # Moviéndose a la izquierda
                    self.rect.left = platform.rect.right
                
                # Colisión vertical
                if dy > 0: # Cayendo
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0: # Saltando y golpeando el techo
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0                
    def update(self, platforms):
        # Aplicar gravedad
        self.vel_y += self.gravity
        
        # Limitar la velocidad de caída máxima
        if self.vel_y > 15:
            self.vel_y = 15
            
        # Controles
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = self.jump_power
            
        # Ejecutar movimiento
        self.move(self.vel_x, self.vel_y, platforms)

        # Evitar que el jugador salga de la pantalla por los lados
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, MARIO_RED, self.rect)

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, GROUND_GREEN, self.rect)

class Goal:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, COIN_GOLD, self.rect)

class Laser:
    def __init__(self, x, y, vel_x, vel_y):
        self.rect = pygame.Rect(x, y, 10, 10) # Ancho de 15px, alto de 5px
        self.vel_x = vel_x
        self.vel_y = vel_y

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self, surface):
        pygame.draw.rect(surface, LASER_RED, self.rect)

class Alien:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.shoot_cooldown = 0 # Temporizador para no disparar en cada frame

    def update(self, player_centerx, player_centery, lasers):
        # Si el temporizador llega a 0, puede disparar
        if self.shoot_cooldown <= 0:
            # Calcula la diferencia de posiciones
            dx = player_centerx - self.rect.centerx
            dy = player_centery - self.rect.centery
            
            #calcular el angulo hacia el jugador
            angle = math.atan2(dy, dx)
            
            # 3. Determinar la velocidad en X y Y basadas en el ángulo
            speed = 7 
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # 4. Crear el láser con esas velocidades
            lasers.append(Laser(self.rect.centerx, self.rect.centery, vel_x, vel_y))
            
            # Reinicia el temporizador (90 frames = 1.5 segundos a 60 FPS)
            self.shoot_cooldown = 60 
        else:
            self.shoot_cooldown -= 1 # Reduce el tiempo de espera

    def draw(self, surface):
        pygame.draw.rect(surface, ALIEN_GREEN, self.rect)

# ---------------------------------------------------------
# 3. Función Principal (Game Loop)
# ---------------------------------------------------------
def main():

    # Instanciar jugador
    player = Player(50, HEIGHT - 100)

    # Crear el nivel (Plataformas)
    platforms = [
        Platform(0, HEIGHT - 40, WIDTH, 40),      # Suelo principal
        Platform(200, 450, 100, 20),              # Plataforma 1
        Platform(350, 350, 100, 20),              # Plataforma 2
        Platform(550, 250, 100, 20),              # Plataforma 3
        Platform(700, 150, 100, 20)               # Plataforma 4 (Alta)
    ]

    # Crear la meta al final del nivel
    goal = Goal(730, 110, 40, 40)

    # Colocamos al marcianito parado sobre la Plataforma 3
    alien = Alien(590, 210) 
    lasers = [] # Lista para almacenar los disparos en pantalla
    
    font = pygame.font.SysFont(None, 48)
    level_complete = False

    running = True
    while running:
        # 1. Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Lógica del juego
        if not level_complete:
            player.update(platforms)
            #detalles marcianito y laseres
            alien.update(player.rect.centerx, player.rect.centery, lasers)
            
            # Usamos [:] para iterar sobre una copia de la lista y poder eliminar elementos sin errores
            for laser in lasers[:]:
                laser.update()
                
                # Si el láser sale de la pantalla, lo borramos para no gastar memoria
                if laser.rect.left < 0 or laser.rect.right > WIDTH or laser.rect.top < 0 or laser.rect.bottom > HEIGHT:
                    lasers.remove(laser)
                # Si el láser choca con el jugador:
                elif laser.rect.colliderect(player.rect):
                    lasers.remove(laser)
                    # Castigo: devolvemos al jugador al inicio
                    player.rect.topleft = (50, HEIGHT - 100)

            # Comprobar si el jugador llegó a la meta
            if player.rect.colliderect(goal.rect):
                level_complete = True
                
            # Comprobar si el jugador cayó al vacío (por si modificas el suelo)
            if player.rect.top > HEIGHT:
                player.rect.topleft = (50, HEIGHT - 100) # Reiniciar posición

        # 3. Dibujado (Render)
        screen.fill(SKY_BLUE) # Fondo
        
        # Dibujar meta y plataformas
        goal.draw(screen)
        for plat in platforms:
            plat.draw(screen)
        #Dibujar marcianito y laseres
        alien.draw(screen)
        for laser in lasers:
            laser.draw(screen)
            
        # Dibujar jugador
        player.draw(screen)

        # Mensaje de victoria
        if level_complete:
            win_text = font.render("¡NIVEL COMPLETADO!", True, TEXT_BLACK)
            screen.blit(win_text, (WIDTH//2 - 180, HEIGHT//2))

        # Actualizar pantalla
        pygame.display.flip()
        
        # Mantener los FPS constantes
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()