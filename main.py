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
pieceValues = {chess.PAWN: 1, chess.BISHOP: 3, chess.KNIGHT: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 9999}
textBox = pygame.Rect(5, 485, 475, 25)
toggleMode = pygame.Rect(5, 575, 75, 20)
EVAL_BAR_RECT = pygame.Rect(480, 0, 20, 480)
EVAL_LABEL_RECT = pygame.Rect(480, 485, 120, 25)
EVAL_BAR_CLAMP = 10  # cap displayed eval at +-10 pawns so the bar never fully empties
GAME_STATUS_RECT = pygame.Rect(5, 515, 475, 30)
RESET_BUTTON_RECT = pygame.Rect(485, 575, 110, 20)

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

dragging = False
drag_square = None
drag_piece = None
_eval_error_printed = False


def square_from_pos(pos):
    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE
    if 0 <= col < 8 and 0 <= row < 8:
        return chess.square(col, 7 - row)
    return None


def get_eval_score(board):
    """Calls evaluate(board) but never lets a bug in it crash the render loop."""
    global _eval_error_printed
    try:
        return evaluate(board)
    except Exception as e:
        if not _eval_error_printed:
            print(f"evaluate() raised an error, showing N/A on the eval bar: {e}")
            _eval_error_printed = True
        return None


def format_eval_label(score):
    if score is None:
        return "N/A"
    sign = "+" if score >= 0 else "-"
    return f"{sign}{abs(score):.2f}"


def draw_eval_bar(screen, board):
    """Vertical bar to the right of the board: white/black fill shows who's
    ahead, scaled to +/- EVAL_BAR_CLAMP pawns, with the raw number below it."""
    score = get_eval_score(board)

    pygame.draw.rect(screen, BLACK, EVAL_BAR_RECT)
    if score is not None:
        clamped = max(-EVAL_BAR_CLAMP, min(EVAL_BAR_CLAMP, score))
        white_fraction = 0.5 + (clamped / EVAL_BAR_CLAMP) / 2
        white_height = int(EVAL_BAR_RECT.height * white_fraction)
        white_rect = pygame.Rect(
            EVAL_BAR_RECT.x,
            EVAL_BAR_RECT.bottom - white_height,
            EVAL_BAR_RECT.width,
            white_height,
        )
        pygame.draw.rect(screen, WHITE, white_rect)

    draw_text_on_rect(screen, format_eval_label(score), EVAL_LABEL_RECT,
                      font, BLACK, pygame.Color((181, 178, 172)))


def main():
    global user_input, textBoxIsActive, inputMode
    global dragging, drag_square, drag_piece
    running = True

    while running:
        clock.tick(60)
        game_over_message = gameOverCheck(board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if RESET_BUTTON_RECT.collidepoint(pygame.mouse.get_pos()):
                    reset_game()
                    continue
                if toggleMode.collidepoint(pygame.mouse.get_pos()):
                    if inputMode == "san":
                        inputMode = "uci"
                        print(inputMode)
                    else:
                        inputMode = "san"
                        print(inputMode)
                elif event.button == 1 and not game_over_message:
                    square = square_from_pos(event.pos)
                    if square is not None and board.piece_at(square):
                        dragging = True
                        drag_square = square
                        drag_piece = board.piece_at(square).symbol()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    target_square = square_from_pos(event.pos)
                    if target_square is not None and target_square != drag_square:
                        move = chess.Move(drag_square, target_square)
                        if move not in board.legal_moves:
                            move = chess.Move(
                                drag_square, target_square, promotion=chess.QUEEN)
                        if move in board.legal_moves:
                            board.push(move)
                        else:
                            print("illegal move, try again")
                    dragging = False
                    drag_square = None
                    drag_piece = None

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
                    if game_over_message:
                        pass
                    elif inputMode == "san":
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
        draw_pieces_from_fen(screen, board.fen(), skip_square=drag_square)
        if dragging and drag_piece is not None:
            piece_img = piece_images[drag_piece]
            mouse_pos = pygame.mouse.get_pos()
            img_rect = piece_img.get_rect(center=mouse_pos)
            screen.blit(piece_img, img_rect)

        draw_eval_bar(screen, board)

        # Draw text box and user input
        pygame.draw.rect(screen, pygame.Color((181, 178, 172)), textBox)
        draw_text_on_rect(screen, user_input,
                          textBox, font, BLACK, WHITE)
        pygame.draw.rect(screen, WHITE, toggleMode)
        draw_text_on_rect(screen, inputMode,
                          toggleMode, font, BLACK, WHITE)

        if game_over_message:
            draw_text_on_rect(screen, game_over_message, GAME_STATUS_RECT,
                              font, WHITE, pygame.Color((109, 79, 75)))
            draw_text_on_rect(screen, "Reset Board", RESET_BUTTON_RECT,
                              font, BLACK, pygame.Color((181, 178, 172)))

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


def draw_pieces_from_fen(screen, fen, skip_square=None):
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
                square = chess.square(col_index, 7 - row_index)
                if square != skip_square:
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
        # board.turn is the side to move, i.e. the side with no legal moves left, i.e. the loser
        return f"Checkmate! {'Black' if board.turn else 'White'} wins!"
    elif board.is_stalemate():
        return "Draw by stalemate"
    elif board.is_insufficient_material():
        return "Draw by insufficient material"
    elif board.is_seventyfive_moves():
        return "Draw by 75-move rule"
    elif board.is_fivefold_repetition():
        return "Draw by fivefold repetition"
    return False


def reset_game():
    global dragging, drag_square, drag_piece, user_input
    board.reset()
    dragging = False
    drag_square = None
    drag_piece = None
    user_input = ""

def evaluate(board):
    white = 0
    black = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece == None:
            continue
        elif piece.color == True:
            white+=pieceValues[piece.piece_type]
        else:
            black+=pieceValues[piece.piece_type]

    return white-black



#this is a straight min max approach, its gonnab be slow but its a good place to start. 
def minmax(depth,maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing_player:
        best_score = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            score = minmax(depth-1, False)
            board.pop()
            best_score = max(best_score, score)

    else:
        best_score = float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = minmax(depth-1, True)
            board.pop()
            best_score = max(best_score)


    



main()
