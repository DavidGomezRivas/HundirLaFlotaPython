import pygame
import pygame_gui
import random
import sys

# Inicializar Pygame y Pygame GUI
pygame.init()
pygame.display.set_caption("Hundir la flota")
screen_width = 1100
screen_height = 600
grid_size = 10
cell_size = 50  # Tamaño de las celdas más grande
screen = pygame.display.set_mode((screen_width, screen_height))
manager = pygame_gui.UIManager((screen_width, screen_height))

# Colores
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Fuente
font = pygame.font.SysFont("Arial", 24)

# Tableros
player1_board = [['~' for _ in range(grid_size)] for _ in range(grid_size)]
player2_board = [['~' for _ in range(grid_size)] for _ in range(grid_size)]
current_turn = 1
placing_ships = True
placing_player = 1
ship_sizes = [5, 4, 3, 3, 2]
current_ship = 0
against_ai = False

# Estados del juego
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_INSTRUCTIONS = "instructions"
game_state = GAME_STATE_MENU

def draw_grid(board, offset_x=0, offset_y=0, show_ships=False):
    for x in range(grid_size):
        for y in range(grid_size):
            rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if board[y][x] == 'H':
                pygame.draw.rect(screen, RED, rect)
            elif board[y][x] == 'M':
                pygame.draw.rect(screen, WHITE, rect)
            elif show_ships and board[y][x] == 'S' and placing_ships:
                pygame.draw.rect(screen, GREEN, rect)

def check_win(board):
    return all(cell != 'S' for row in board for cell in row)

def reset_game():
    global player1_board, player2_board, current_turn, message, placing_ships, placing_player, current_ship, against_ai
    player1_board = [['~' for _ in range(grid_size)] for _ in range(grid_size)]
    player2_board = [['~' for _ in range(grid_size)] for _ in range(grid_size)]
    current_turn = 1
    placing_ships = True
    placing_player = 1
    current_ship = 0
    message = "Jugador 1, coloca tus barcos"
    if against_ai:
        place_ships_randomly(player2_board)

def draw_ship_placement_instructions():
    instructions = [
        "1. Haz clic en una celda para colocar el barco horizontalmente.",
        "2. Los barcos no pueden solaparse ni salirse del tablero."
    ]
    for i, line in enumerate(instructions):
        label = font.render(line, True, BLACK)
        screen.blit(label, (screen_width // 2 - 250, screen_height - 70 + i * 30))

def place_ships_randomly(board):
    for size in ship_sizes:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            orientation = random.choice(['horizontal', 'vertical'])
            if orientation == 'horizontal':
                x = random.randint(0, grid_size - size)
                y = random.randint(0, grid_size - 1)
                if all(board[y][x + i] == '~' for i in range(size)):
                    for i in range(size):
                        board[y][x + i] = 'S'
                    placed = True
            else:
                x = random.randint(0, grid_size - 1)
                y = random.randint(0, grid_size - size)
                if all(board[y + i][x] == '~' for i in range(size)):
                    for i in range(size):
                        board[y + i][x] = 'S'
                    placed = True
            attempts += 1

def ai_move():
    global message, current_turn
    while True:
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        if player1_board[y][x] not in ['H', 'M']:
            break
    if player1_board[y][x] == 'S':
        player1_board[y][x] = 'H'
        message = "¡La IA acertó!"
        if check_win(player1_board):
            message = "¡La IA ganó!"
            dialog = pygame_gui.windows.UIConfirmationDialog(
                rect=pygame.Rect((150, 200), (300, 200)),
                manager=manager,
                window_title="Ganaste",
                action_long_desc="¡La IA ha hundido todos los barcos! ¿Quieres jugar otra partida?",
                action_short_name="Reiniciar",
                blocking=True
            )
            dialog.confirm_button.set_text("Reiniciar")
            dialog.cancel_button.set_text("No")
        else:
            ai_move()  # Hacer otro movimiento si acierta
    else:
        player1_board[y][x] = 'M'
        message = "Jugador 1, haz un disparo"
        current_turn = 1

# Crear botones del menú
def create_menu_buttons():
    play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((screen_width // 2 - 75, screen_height // 2 - 100), (150, 50)),
                                               text='Jugar',
                                               manager=manager)
    play_ai_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((screen_width // 2 - 75, screen_height // 2 - 50), (150, 50)),
                                                  text='Jugar contra IA',
                                                  manager=manager)
    instructions_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((screen_width // 2 - 75, screen_height // 2), (150, 50)),
                                                       text='Cómo jugar',
                                                       manager=manager)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((screen_width // 2 - 75, screen_height // 2 + 50), (150, 50)),
                                               text='Salir',
                                               manager=manager)
    return play_button, play_ai_button, instructions_button, quit_button

play_button, play_ai_button, instructions_button, quit_button = create_menu_buttons()

running = True
clock = pygame.time.Clock()

back_button = None

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play_button:
                    game_state = GAME_STATE_PLAYING
                    against_ai = False
                    reset_game()
                    manager.clear_and_reset()
                elif event.ui_element == play_ai_button:
                    game_state = GAME_STATE_PLAYING
                    against_ai = True
                    reset_game()
                    manager.clear_and_reset()
                elif event.ui_element == instructions_button:
                    game_state = GAME_STATE_INSTRUCTIONS
                    manager.clear_and_reset()
                    back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((screen_width // 2 - 75, screen_height - 70), (150, 50)),
                                                               text='Volver',
                                                               manager=manager)
                elif event.ui_element == quit_button:
                    running = False
                    sys.exit()
                elif game_state == GAME_STATE_PLAYING and event.ui_element == dialog.confirm_button:
                    reset_game()
                elif game_state == GAME_STATE_PLAYING and event.ui_element == dialog.cancel_button:
                    running = False
                    sys.exit()
                elif game_state == GAME_STATE_INSTRUCTIONS and event.ui_element == back_button:
                    game_state = GAME_STATE_MENU
                    manager.clear_and_reset()
                    play_button, play_ai_button, instructions_button, quit_button = create_menu_buttons()

        elif game_state == GAME_STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if placing_ships:
                    board = player1_board if placing_player == 1 else player2_board
                    if y < screen_height and (placing_player == 1 or not against_ai):
                        if placing_player == 2:
                            x -= screen_width // 2 + 50
                        x = x // cell_size
                        y = y // cell_size
                        if 0 <= x < grid_size and 0 <= y < grid_size:
                            size = ship_sizes[current_ship]
                            if x + size <= grid_size and all(board[y][x + i] == '~' for i in range(size)):
                                for i in range(size):
                                    board[y][x + i] = 'S'
                                current_ship += 1
                                if current_ship >= len(ship_sizes):
                                    if placing_player == 1:
                                        placing_player = 2
                                        current_ship = 0
                                        message = "Jugador 2, coloca tus barcos"
                                        if against_ai:
                                            place_ships_randomly(player2_board)
                                            placing_ships = False
                                            message = "Jugador 1, haz un disparo"
                                    else:
                                        placing_ships = False
                                        message = "Jugador 1, haz un disparo"
                elif not placing_ships:
                    if current_turn == 1 and y < screen_height and x > screen_width // 2 + 50:
                        x = (x - (screen_width // 2 + 50)) // cell_size
                        y = y // cell_size
                        if 0 <= x < grid_size and 0 <= y < grid_size:
                            if player2_board[y][x] == 'S':
                                player2_board[y][x] = 'H'
                                message = "¡Jugador 1 acertó!"
                                if check_win(player2_board):
                                    message = "¡Jugador 1 ganó!"
                                    dialog = pygame_gui.windows.UIConfirmationDialog(
                                        rect=pygame.Rect((150, 200), (300, 200)),
                                        manager=manager,
                                        window_title="Ganaste",
                                        action_long_desc="¡Jugador 1 ha hundido todos los barcos! ¿Quieres jugar otra partida?",
                                        action_short_name="Reiniciar",
                                        blocking=True
                                    )
                                    dialog.confirm_button.set_text("Reiniciar")
                                    dialog.cancel_button.set_text("No")
                            elif player2_board[y][x] == '~':
                                player2_board[y][x] = 'M'
                                if against_ai:
                                    current_turn = 2
                                    ai_move()
                                else:
                                    message = "Jugador 2, haz un disparo"
                                    current_turn = 2
                    elif current_turn == 2 and not against_ai and y < screen_height and x < screen_width // 2 - 50:
                        x = x // cell_size
                        y = y // cell_size
                        if 0 <= x < grid_size and 0 <= y < grid_size:
                            if player1_board[y][x] == 'S':
                                player1_board[y][x] = 'H'
                                message = "¡Jugador 2 acertó!"
                                if check_win(player1_board):
                                    message = "¡Jugador 2 ganó!"
                                    dialog = pygame_gui.windows.UIConfirmationDialog(
                                        rect=pygame.Rect((150, 200), (300, 200)),
                                        manager=manager,
                                        window_title="Ganaste",
                                        action_long_desc="¡Jugador 2 ha hundido todos los barcos! ¿Quieres jugar otra partida?",
                                        action_short_name="Reiniciar",
                                        blocking=True
                                    )
                                    dialog.confirm_button.set_text("Reiniciar")
                                    dialog.cancel_button.set_text("No")
                            elif player1_board[y][x] == '~':
                                player1_board[y][x] = 'M'
                                message = "Jugador 1, haz un disparo"
                                current_turn = 1

        manager.process_events(event)

    screen.fill(BLUE)

    if game_state == GAME_STATE_MENU:
        title = font.render("Hundir la flota", True, WHITE)
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 100))
    elif game_state == GAME_STATE_PLAYING:
        draw_grid(player1_board, show_ships=placing_ships and placing_player == 1)
        draw_grid(player2_board, offset_x=screen_width // 2 + 50, show_ships=placing_ships and placing_player == 2)
        label = font.render(message, True, BLACK)
        screen.blit(label, (screen_width // 2 - 200, screen_height + 10))
        if placing_ships:
            draw_ship_placement_instructions()
    elif game_state == GAME_STATE_INSTRUCTIONS:
        instructions = [
            "Instrucciones de juego:",
            "1. Coloca tus barcos en el tablero.",
            "2. Los barcos no pueden solaparse ni salirse del tablero.",
            "3. Los jugadores se turnan para disparar a las coordenadas del enemigo.",
            "4. El primer jugador en hundir todos los barcos enemigos gana."
        ]
        for i, line in enumerate(instructions):
            label = font.render(line, True, WHITE)
            screen.blit(label, (screen_width // 2 - 250, 100 + i * 30))

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
