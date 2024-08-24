import pygame
import chess

board = chess.Board()

print(board)
STARTING_FEN = chess.STARTING_FEN
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (109, 79, 75)
LIGHT_BROWN = (237, 201, 175)
SQUARE_SIZE = 60
HIGHLIGHT_COLOR = (255, 0, 0)  # Red color for the border when hovered
coordDict = {'a': 0, 'b': 60, 'c': 120, 'd': 180,
             'e': 240, 'f': 300, 'g': 360, 'h': 420}
numberDict = {'1': 420, '2': 360, '3': 300,
              '4': 240, '5': 180, '6': 120, '7': 60, '8': 0}
textBox = pygame.Rect(5, 485, 475, 25)
toggleMode = pygame.Rect(5, 575, 75, 20)

piece_images = {
    'r': pygame.image.load("media/black_rook.png"),
    'n': pygame.image.load("media/black_knight.png"),
    'b': pygame.image.load("media/black_bishop.png"),
    'q': pygame.image.load("media/black_queen.png"),
    'k': pygame.image.load("media/black_king.png"),
    'p': pygame.image.load("media/black_pawn.png"),
    'R': pygame.image.load("media/white_rook.png"),
    'N': pygame.image.load("media/white_knight.png"),
    'B': pygame.image.load("media/white_bishop.png"),
    'Q': pygame.image.load("media/white_queen.png"),
    'K': pygame.image.load("media/white_king.png"),
    'P': pygame.image.load("media/white_pawn.png")
}

pygame.init()
font = pygame.font.Font(None, 24)
screen = pygame.display.set_mode((600, 600))
pygame.display.set_icon(pygame.image.load("media/black_knight.png"))
pygame.display.set_caption("Chess GUI")
clock = pygame.time.Clock()
inputMode = "san"
# Variable to hold the user input
user_input = ""
textBoxIsActive = False  # Track if text box is active


def main():
    global user_input, textBoxIsActive, inputMode
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if toggleMode.collidepoint(pygame.mouse.get_pos()):
                    if inputMode == "san":
                        inputMode = "uci"
                        print(inputMode)
                    else:
                        inputMode = "san"
                        print(inputMode)
            # Check if mouse clicks on the text box

            # Handle keyboard input when the text box is active
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    # Remove the last character from user input
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    # For Enter key, deactivate text box
                    userMove = user_input
                    user_input = ""

                    print(userMove)
                    if inputMode == "san":
                        if is_legal_san_move(board, userMove):
                            board.push_san(userMove)
                        else:
                            print("illegal move, try again")
                    elif inputMode == "uci":
                        if is_legal_uci_move(board, userMove):
                            board.push_uci(userMove)
                        else:
                            print("illegal move, try again")
                else:
                    # Add character to user input
                    user_input += event.unicode

        screen.fill(color=(46, 43, 38))
        drawBoard(screen)

        get_square_under_mouse(screen)
        draw_pieces_from_fen(screen, board.fen())

        # Draw text box and user input
        pygame.draw.rect(screen, pygame.Color((181, 178, 172)), textBox)
        draw_text_on_rect(screen, user_input,
                          textBox, font, BLACK, WHITE)
        pygame.draw.rect(screen, WHITE, toggleMode)
        draw_text_on_rect(screen, inputMode,
                          toggleMode, font, BLACK, WHITE)
        pygame.display.flip()


def is_legal_uci_move(board, uci_move):
    try:
        # Convert the UCI move string into a move object
        move = chess.Move.from_uci(uci_move)

        # Check if the move is legal
        if move in board.legal_moves:
            return True
        else:
            return False
    except:
        # If the UCI move format is invalid or can't be parsed
        return False


def is_legal_san_move(board, san_move):
    try:
        # Convert the SAN move to a Move object
        move = board.parse_san(san_move)

        # Check if the move is in the list of legal moves
        if move in board.legal_moves:
            return True
        else:
            return False
    except ValueError:
        # If the SAN move is invalid or can't be parsed
        return False


def draw_pieces_from_fen(screen, fen):
    """Takes a FEN string and draws the pieces on the board."""
    fen_parts = fen.split(
        " ")[0]  # Extract only the board layout from the FEN string
    ranks = fen_parts.split("/")

    for row_index, rank in enumerate(ranks):
        col_index = 0
        for char in rank:
            if char.isdigit():
                # Empty squares (advance by the number of empty squares)
                col_index += int(char)
            else:
                # There's a piece to draw
                # Fetch the correct image based on the FEN char
                piece = piece_images[char]
                x = col_index * SQUARE_SIZE
                y = row_index * SQUARE_SIZE
                screen.blit(piece, (x, y))
                col_index += 1


def draw_text_on_rect(screen, text, rect, font, text_color, bg_color):
    # Draw the rectangle
    pygame.draw.rect(screen, bg_color, rect)

    # Render the text
    text_surface = font.render(text, True, text_color)

    # Center the text on the rectangle
    text_rect = text_surface.get_rect(center=rect.center)

    # Blit the text onto the rectangle
    screen.blit(text_surface, text_rect)


def drawBoard(screen):
    # Draws an 8x8 chessboard using alternating colors.
    for row in range(8):
        for col in range(8):
            # Alternate between two colors
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def get_square_under_mouse(screen):
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    for row in range(8):
        for col in range(8):
            square_rect = pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if square_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                                 square_rect, 3)  # Draw a red border


def gameOverCheck(board):
    if board.is_checkmate():
        return f"Checkmate! {'White' if board.turn else 'Black'} wins!"
    elif board.is_stalemate():
        return "stalemate"
    elif board.is_insufficient_material():
        return "insufficient"
    elif board.is_seventyfive_moves():
        return "75"
    elif board.is_fivefold_repetition():
        return "fivefold"
    return False


main()
