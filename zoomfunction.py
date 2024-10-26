import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zoom Slider Example")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# Load an image or create a surface
content_surface = pygame.Surface((600, 400))
content_surface.fill(WHITE)
for i in range(0, 600, 50):
    pygame.draw.rect(content_surface, BLACK, (i, 50, 40, 300), 2)

# Slider properties
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 10
slider_rect = pygame.Rect((SCREEN_WIDTH - SLIDER_WIDTH) // 2, SCREEN_HEIGHT - 100, SLIDER_WIDTH, SLIDER_HEIGHT)
slider_handle_rect = pygame.Rect(slider_rect.x, slider_rect.y - 5, 20, SLIDER_HEIGHT + 10)

# Zoom properties
zoom_level = 1.0  # Initial zoom level (1.0 means 100%)
min_zoom = 0.5
max_zoom = 2.0

# Main loop
running = True
dragging = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Handle slider input
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if slider_handle_rect.collidepoint(event.pos):
                dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                # Adjust the slider handle's position based on mouse position
                slider_handle_rect.x = max(slider_rect.x, min(event.pos[0], slider_rect.x + SLIDER_WIDTH - slider_handle_rect.width))
                
                # Calculate the zoom level based on the slider handle's position
                slider_percentage = (slider_handle_rect.x - slider_rect.x) / (SLIDER_WIDTH - slider_handle_rect.width)
                zoom_level = min_zoom + slider_percentage * (max_zoom - min_zoom)

    # Draw everything
    SCREEN.fill(WHITE)
    
    # Scale the content surface based on zoom level
    zoomed_width = int(content_surface.get_width() * zoom_level)
    zoomed_height = int(content_surface.get_height() * zoom_level)
    zoomed_surface = pygame.transform.smoothscale(content_surface, (zoomed_width, zoomed_height))

    # Center the zoomed surface on the screen
    zoomed_rect = zoomed_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    SCREEN.blit(zoomed_surface, zoomed_rect)

    # Draw the slider background
    pygame.draw.rect(SCREEN, GRAY, slider_rect)
    # Draw the slider handle
    pygame.draw.rect(SCREEN, DARK_GRAY, slider_handle_rect)

    # Draw the zoom level text
    font = pygame.font.Font(None, 36)
    zoom_text = font.render(f"Zoom: {int(zoom_level * 100)}%", True, BLACK)
    SCREEN.blit(zoom_text, (SCREEN_WIDTH // 2 - zoom_text.get_width() // 2, slider_rect.y - 40))

    # Update the display
    pygame.display.update()
