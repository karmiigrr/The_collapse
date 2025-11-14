import pygame
import sys

# Inicializar pygame
pygame.init()

# --- Configuración de la ventana ---
ANCHO_PANTALLA = 1920
ALTO_PANTALLA = 1080
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Mapa largo estilo Hollow Knight")

# --- Colores ---
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

# --- Cargar fondos ---
fondo1 = pygame.image.load("fondo1.jpg").convert()
fondo2 = pygame.image.load("fondo2.jpg").convert()

# --- Configuración del personaje ---
TAM_PERSONAJE = (64, 64)
personaje_img_original = pygame.image.load("personaje.png").convert_alpha()
zoom = 1.2
nuevo_tam = (int(TAM_PERSONAJE[0] * zoom), int(TAM_PERSONAJE[1] * zoom))
personaje_img = pygame.transform.scale(personaje_img_original, nuevo_tam)
personaje_rect = personaje_img.get_rect()

# Posición inicial habitación 1 y 2
pos_inicial_h1 = (2100, 400)
pos_inicial_h2 = (2800, 400)
personaje_rect.midbottom = pos_inicial_h1

# --- Plataformas ---
plataformas_habitacion1 = [
    pygame.Rect(0, 560, 970, 100),
    pygame.Rect(1000, 725, 325, 40),
    pygame.Rect(1475, 850, 270, 40),
    pygame.Rect(1875, 800, 500, 100),
]

plataformas_habitacion2 = [
    pygame.Rect(600, 720, 1400, 100),
    pygame.Rect(2100, 500, 1000, 40),
]

# --- Movimiento ---
velocidad = 4
cam_x = 0
vel_y = 0
gravedad = 1
fuerza_salto = -20
en_suelo = True

# --- Reloj ---
clock = pygame.time.Clock()

# --- Variables globales ---
habitacion_actual = 1
juego_pausado = False

# =====================================================
# ============= PANTALLA DE INTRODUCCIÓN ==============
# =====================================================
intro_img = pygame.image.load("intro.jpg").convert()
intro_img = pygame.transform.scale(intro_img, (ANCHO_PANTALLA, ALTO_PANTALLA))


def mostrar_intro():
    fuente = pygame.font.Font(None, 100)
    texto = fuente.render("Presiona cualquier tecla para comenzar", True, BLANCO)
    texto_rect = texto.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA - 200))

    mostrando = True
    while mostrando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                mostrando = False

        pantalla.blit(intro_img, (0, 0))
        pantalla.blit(texto, texto_rect)
        pygame.display.flip()
        clock.tick(30)


def transicion(fondo_actual, cam_x, personaje_rect):
    fade = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    fade.fill(NEGRO)
    for alpha in range(0, 256, 15):
        fade.set_alpha(alpha)
        pantalla.blit(fondo_actual, (-cam_x, 0))
        pantalla.blit(personaje_img, (personaje_rect.x - cam_x, personaje_rect.y - nuevo_tam[1]))
        pantalla.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    for alpha in range(255, -1, -15):
        fade.set_alpha(alpha)
        pantalla.blit(fondo_actual, (-cam_x, 0))
        pantalla.blit(personaje_img, (personaje_rect.x - cam_x, personaje_rect.y - nuevo_tam[1]))
        pantalla.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def mostrar_pausa():
    fuente = pygame.font.Font(None, 120)
    texto = fuente.render("PAUSA", True, BLANCO)
    texto_rect = texto.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA//2 - 100))

    fuente2 = pygame.font.Font(None, 60)
    texto2 = fuente2.render("Presiona ESC para reanudar o Q para salir", True, BLANCO)
    texto2_rect = texto2.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA//2 + 100))

    overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    pantalla.blit(overlay, (0, 0))
    pantalla.blit(texto, texto_rect)
    pantalla.blit(texto2, texto2_rect)
    pygame.display.flip()


# --- Mostrar introducción ---
mostrar_intro()

# =====================================================
# ================= BUCLE PRINCIPAL ===================
# =====================================================

# --- Configuración del NPC ---
class NPC:
    def __init__(self, x, y, imagen):
        self.x = x
        self.y = y
        self.imagen = imagen
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y))
    
    def dibujar(self, pantalla, cam_x):
        pantalla.blit(self.imagen, (self.x - cam_x, self.y))  # Dibujamos el NPC en pantalla, ajustando la cámara

# Cargar la imagen del NPC
npc_imagen = pygame.image.load("npc.png").convert_alpha()
npc_imagen = pygame.transform.scale(npc_imagen, (200, 100))  # Ajusta el tamaño si es necesario
npc = NPC(1500, 650, npc_imagen)  # Posición del NPC

# --- Mensaje de interacción ---
mostrar_mensaje = False
mensaje = "Presiona E para hablar"
dialogo_estado = 0  # Estado de diálogo (0: sin interacción, 1: mostrando elecciones, 2: mostrando respuesta)

respuesta_npc = ""

# Opciones de diálogo
opciones = {
    1: "¿Cómo estás?",
    2: "¿Qué haces aquí?"
}

# Respuestas del NPC
respuestas = {
    1: "Estoy bien, gracias por preguntar.",
    2: "Estoy esperando a que alguien me hable."
}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Pausa
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                juego_pausado = not juego_pausado
            if juego_pausado and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            # Interacción con el NPC
            if mostrar_mensaje and event.key == pygame.K_e:
                dialogo_estado = 1  # Mostrar las opciones de diálogo

            # Selección de opción
            if dialogo_estado == 1:
                if event.key == pygame.K_1:
                    respuesta_npc = respuestas[1]
                    dialogo_estado = 2  # Mostrar la respuesta
                elif event.key == pygame.K_2:
                    respuesta_npc = respuestas[2]
                    dialogo_estado = 2  # Mostrar la respuesta

            # Cerrar el diálogo con ESC
            if event.key == pygame.K_ESCAPE:
                dialogo_estado = 0
                respuesta_npc = ""

    if juego_pausado:
        mostrar_pausa()
        continue

    # Movimiento del personaje
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a]:
        personaje_rect.x -= velocidad
    if teclas[pygame.K_d]:
        personaje_rect.x += velocidad

    # Saltar
    if teclas[pygame.K_SPACE] and en_suelo:
        vel_y = fuerza_salto
        en_suelo = False

    # Aplicar gravedad
    vel_y += gravedad
    personaje_rect.y += vel_y

    # Determinar plataformas según la habitación
    if habitacion_actual == 1:
        plataformas = plataformas_habitacion1
        fondo = fondo1
    else:
        plataformas = plataformas_habitacion2
        fondo = fondo2

    # Colisiones
    en_suelo = False
    for plataforma in plataformas:
        if personaje_rect.colliderect(plataforma):
            if vel_y > 0 and personaje_rect.bottom - vel_y <= plataforma.top:
                personaje_rect.bottom = plataforma.top
                vel_y = 0
                en_suelo = True

    # Cambio de habitación con transición
    if habitacion_actual == 1 and personaje_rect.left <= 0:
        transicion(fondo, cam_x, personaje_rect)
        habitacion_actual = 2
        personaje_rect.midbottom = pos_inicial_h2
        vel_y = 0
    elif habitacion_actual == 2 and personaje_rect.right >= fondo.get_width():
        transicion(fondo, cam_x, personaje_rect)
        habitacion_actual = 1
        personaje_rect.midbottom = pos_inicial_h1
        vel_y = 0

    # Caída al vacío
    if personaje_rect.top > ALTO_PANTALLA:
        transicion(fondo, cam_x, personaje_rect)
        personaje_rect.midbottom = pos_inicial_h1
        vel_y = 0
        en_suelo = True
        habitacion_actual = 1

    # Cámara
    cam_x = personaje_rect.centerx - ANCHO_PANTALLA // 2
    cam_x = max(0, min(cam_x, fondo.get_width() - ANCHO_PANTALLA))

    # --- Comprobar proximidad al NPC ---
    if habitacion_actual == 1 and personaje_rect.colliderect(npc.rect):
        mostrar_mensaje = True
    else:
        mostrar_mensaje = False

    # --- Dibujar ---
    pantalla.fill(NEGRO)
    pantalla.blit(fondo, (-cam_x, 0))
    pantalla.blit(personaje_img, (personaje_rect.x - cam_x, personaje_rect.y - nuevo_tam[1]))

    # Dibujamos al NPC solo si estamos en la habitación 1
    if habitacion_actual == 1:
        npc.dibujar(pantalla, cam_x)

    # Si está cerca del NPC, mostrar el mensaje
    if mostrar_mensaje and dialogo_estado == 0:
        fuente = pygame.font.Font(None, 40)
        texto = fuente.render(mensaje, True, BLANCO)
        texto_rect = texto.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA - 100))
        pantalla.blit(texto, texto_rect)

    # Mostrar opciones de diálogo
    if dialogo_estado == 1:
        fuente = pygame.font.Font(None, 40)
        texto = fuente.render("1. ¿Cómo estás?  2. ¿Qué haces aquí?", True, BLANCO)
        texto_rect = texto.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA - 200))
        pantalla.blit(texto, texto_rect)

    # Mostrar respuesta del NPC
    if dialogo_estado == 2:
        fuente = pygame.font.Font(None, 40)
        texto = fuente.render(respuesta_npc, True, BLANCO)
        texto_rect = texto.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA - 200))
        pantalla.blit(texto, texto_rect)

    pygame.display.flip()
    clock.tick(60)
