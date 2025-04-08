import pygame
import pyperclip

# Instellingen
BACKGROUND_IMAGE = "assets/background.webp"  # Zorg dat dit een 3456x2160 foto is
WINDOW_TITLE = "Klik om coördinaten te pakken"

pygame.init()

# Game-resolutie (en dus ons coördinatensysteem)
GAME_WIDTH, GAME_HEIGHT = 1920, 1200
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Laad de originele afbeelding (3456x2160)
bg_original = pygame.image.load(BACKGROUND_IMAGE).convert()
IMAGE_WIDTH, IMAGE_HEIGHT = bg_original.get_size()  # 3456x2160

# Bereken de schaalfactor voor het omzetten van origineel naar game-coördinaten
factor = GAME_WIDTH / IMAGE_WIDTH  # Dit geldt ook voor de hoogte (0.5555...)

# Camera instellingen (voor zoom en pan)
zoom = 1.0
min_zoom, max_zoom = 0.2, 5.0
camera_x, camera_y = 0, 0
pan_speed = 20

font = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()
# Hier slaan we de game-coördinaten op (dus in het 1920x1200-systeem)
coords = []

def draw():
    # Schaal de originele afbeelding met de huidige zoomfactor
    scaled_img = pygame.transform.smoothscale(bg_original, (int(IMAGE_WIDTH * zoom), int(IMAGE_HEIGHT * zoom)))
    # Teken de afbeelding op basis van pan (camera_x, camera_y)
    screen.blit(scaled_img, (-camera_x, -camera_y))
    
    # Teken de markers
    for gx, gy in coords:
        # Eerst: zet de game-coördinaten om naar originele afbeeldingscoördinaten
        orig_x = gx / factor
        orig_y = gy / factor
        # Vervolgens: bereken de positie op het scherm (met zoom en pan)
        screen_x = int(orig_x * zoom) - camera_x
        screen_y = int(orig_y * zoom) - camera_y
        pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 3)
        label = font.render(f"({gx}, {gy})", True, (255, 255, 255))
        screen.blit(label, (screen_x + 5, screen_y - 10))

def get_game_coords(mouse_x, mouse_y):
    """
    Zet een klik in schermcoördinaten (GAME_WIDTH, GAME_HEIGHT) om naar de 
    originele afbeeldingscoördinaten en vervolgens naar game-coördinaten.
    """
    # Eerst: omrekenen naar originele afbeeldingscoördinaten (3456x2160)
    orig_x = (mouse_x + camera_x) / zoom
    orig_y = (mouse_y + camera_y) / zoom
    # Nu: omrekenen naar game-coördinaten door te schalen met 'factor'
    game_x = orig_x * factor
    game_y = orig_y * factor
    return int(game_x), int(game_y)

def export_coords_yaml(coords):
    yaml_lines = [f"  - [{x}, {y}]" for x, y in coords]
    yaml_text = "\n".join(yaml_lines)
    pyperclip.copy(yaml_text)
    print("\n📋 Gekopieerd naar klembord:\n" + yaml_text)

running = True
while running:
    screen.fill((0, 0, 0))
    draw()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_BACKSPACE and coords:
                coords.pop()
            elif event.key == pygame.K_e:
                export_coords_yaml(coords)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Linkerklik
                mx, my = pygame.mouse.get_pos()
                game_coords = get_game_coords(mx, my)
                coords.append(game_coords)
                pyperclip.copy(f"[{game_coords[0]}, {game_coords[1]}]")
                print(f"🖱️ Klik: scherm=({mx}, {my}) -> game-coördinaten = {game_coords}")
            elif event.button == 4:  # Zoom in
                mx, my = pygame.mouse.get_pos()
                pre_zoom = ((mx + camera_x) / zoom, (my + camera_y) / zoom)
                zoom = min(zoom * 1.1, max_zoom)
                camera_x = int(pre_zoom[0] * zoom - mx)
                camera_y = int(pre_zoom[1] * zoom - my)
            elif event.button == 5:  # Zoom uit
                mx, my = pygame.mouse.get_pos()
                pre_zoom = ((mx + camera_x) / zoom, (my + camera_y) / zoom)
                zoom = max(zoom / 1.1, min_zoom)
                camera_x = int(pre_zoom[0] * zoom - mx)
                camera_y = int(pre_zoom[1] * zoom - my)
    
    # Panning met pijltjestoetsen
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= pan_speed
    if keys[pygame.K_RIGHT]:
        camera_x += pan_speed
    if keys[pygame.K_UP]:
        camera_y -= pan_speed
    if keys[pygame.K_DOWN]:
        camera_y += pan_speed

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
