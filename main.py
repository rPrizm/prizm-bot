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
coordDict = {'a': 0, 'b': 60, 'c': 120, 'd': 180,
             'e': 240, 'f': 300, 'g': 360, 'h': 420}
numberDict = {'1': 420, '2': 360, '3': 300,
              '4': 240, '5': 180, '6': 120, '7': 60, '8': 0}
pieceValues = {chess.PAWN: 1, chess.BISHOP: 3, chess.KNIGHT: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 9999}



# --- Modern dark theme palette -------------------------------------------------
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 608
BG_COLOR = (18, 19, 23)
CARD_COLOR = (33, 36, 43)
INSET_COLOR = (46, 50, 59)
BORDER_COLOR = (58, 63, 74)
ACCENT_COLOR = (94, 170, 255)
ACCENT_HOVER_COLOR = (128, 191, 255)
DANGER_COLOR = (235, 87, 87)
TEXT_PRIMARY = (235, 236, 240)
TEXT_MUTED = (150, 155, 165)
CARD_RADIUS = 20
BUTTON_RADIUS = 12

# --- Layout ---------------------------------------------------------------------
APP_CARD_RECT = pygame.Rect(10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20)
BOARD_ORIGIN = (20, 20)
BOARD_SIZE = SQUARE_SIZE * 8

EVAL_BAR_RECT = pygame.Rect(BOARD_ORIGIN[0] + BOARD_SIZE + 14, BOARD_ORIGIN[1], 26, BOARD_SIZE)
EVAL_LABEL_RECT = pygame.Rect(EVAL_BAR_RECT.centerx - 38, BOARD_ORIGIN[1] + BOARD_SIZE + 8, 76, 30)
EVAL_BAR_CLAMP = 10  # cap displayed eval at +-10 pawns so the bar never fully empties

GAME_STATUS_RECT = pygame.Rect(20, 520, 458, 40)
RESET_BUTTON_RECT = pygame.Rect(490, 520, 90, 40)

MENU_CARD_RECT = pygame.Rect(100, 150, 400, 350)
MENU_PLAY_WHITE_RECT = pygame.Rect(140, 300, 320, 64)
MENU_PLAY_BLACK_RECT = pygame.Rect(140, 380, 320, 64)

STATE_MENU = "menu"
STATE_PLAYING = "playing"

ENGINE_SEARCH_DEPTH = 3

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
pygame.mixer.init()
font = pygame.font.Font("media/fonts/Poppins-Medium.ttf", 20)
small_font = pygame.font.Font("media/fonts/Poppins-Regular.ttf", 16)
title_font = pygame.font.Font("media/fonts/Poppins-SemiBold.ttf", 32)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_icon(pygame.image.load("media/black_knight.png"))
pygame.display.set_caption("Chess GUI")
clock = pygame.time.Clock()
dragging = False
drag_square = None
drag_piece = None
_eval_error_printed = False

game_state = STATE_MENU
player_side = chess.WHITE
board_flipped = False

menu_king_icons = {
    chess.WHITE: pygame.transform.smoothscale(piece_images['K'], (40, 40)),
    chess.BLACK: pygame.transform.smoothscale(piece_images['k'], (40, 40)),
}

# Sound effects sourced from lichess's "standard" theme (lichess-org/lila,
# public/sound/standard, AGPL-3.0). Lichess itself has no distinct check or
# checkmate sound: every move just plays its move/capture sound, and a single
# generic chime marks the game ending (checkmate, stalemate, draw, etc).
sounds = {
    "move": pygame.mixer.Sound("media/sounds/move.ogg"),
    "capture": pygame.mixer.Sound("media/sounds/capture.ogg"),
    "end": pygame.mixer.Sound("media/sounds/end.ogg"),
}


def push_move_with_sound(board, move):
    was_capture = board.is_capture(move)
    board.push(move)
    (sounds["capture"] if was_capture else sounds["move"]).play()
    if board.is_game_over():
        sounds["end"].play()


def square_from_pos(pos):
    col = (pos[0] - BOARD_ORIGIN[0]) // SQUARE_SIZE
    row = (pos[1] - BOARD_ORIGIN[1]) // SQUARE_SIZE
    if 0 <= col < 8 and 0 <= row < 8:
        if board_flipped:
            return chess.square(7 - col, row)
        return chess.square(col, 7 - row)
    return None


def screen_pos_for_square(square):
    """Returns the (x, y) top-left pixel for a square, respecting board_flipped."""
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    if board_flipped:
        col = 7 - file_index
        row = rank_index
    else:
        col = file_index
        row = 7 - rank_index
    return BOARD_ORIGIN[0] + col * SQUARE_SIZE, BOARD_ORIGIN[1] + row * SQUARE_SIZE


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

    pygame.draw.rect(screen, INSET_COLOR, EVAL_BAR_RECT, border_radius=BUTTON_RADIUS)
    if score is not None:
        clamped = max(-EVAL_BAR_CLAMP, min(EVAL_BAR_CLAMP, score))
        white_fraction = 0.5 + (clamped / EVAL_BAR_CLAMP) / 2
        white_height = int(EVAL_BAR_RECT.height * white_fraction)
        white_height = max(0, min(EVAL_BAR_RECT.height, white_height))
        if white_height > 0:
            white_rect = pygame.Rect(
                EVAL_BAR_RECT.x,
                EVAL_BAR_RECT.bottom - white_height,
                EVAL_BAR_RECT.width,
                white_height,
            )
            # The fill always touches the track's bottom edge, so its bottom
            # corners should always match the track's rounding; its top
            # corners only round once the fill reaches all the way up.
            full = white_height >= EVAL_BAR_RECT.height
            pygame.draw.rect(
                screen, WHITE, white_rect,
                border_bottom_left_radius=BUTTON_RADIUS,
                border_bottom_right_radius=BUTTON_RADIUS,
                border_top_left_radius=BUTTON_RADIUS if full else 0,
                border_top_right_radius=BUTTON_RADIUS if full else 0,
            )

    draw_text_centered(screen, format_eval_label(score), small_font, TEXT_MUTED, EVAL_LABEL_RECT.center)


def draw_menu(screen):
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, CARD_COLOR, MENU_CARD_RECT, border_radius=CARD_RADIUS)

    title_center = (MENU_CARD_RECT.centerx, MENU_CARD_RECT.top + 60)
    draw_text_centered(screen, "Choose Your Side", title_font, TEXT_PRIMARY, title_center)

    subtitle_center = (MENU_CARD_RECT.centerx, MENU_CARD_RECT.top + 110)
    draw_text_centered(screen, "The engine will play the other side", small_font, TEXT_MUTED, subtitle_center)

    mouse_pos = pygame.mouse.get_pos()
    draw_icon_button(screen, MENU_PLAY_WHITE_RECT, "Play as White", menu_king_icons[chess.WHITE],
                      hovered=MENU_PLAY_WHITE_RECT.collidepoint(mouse_pos))
    draw_icon_button(screen, MENU_PLAY_BLACK_RECT, "Play as Black", menu_king_icons[chess.BLACK],
                      hovered=MENU_PLAY_BLACK_RECT.collidepoint(mouse_pos))


def start_game_as(side):
    global player_side, board_flipped, game_state
    player_side = side
    board_flipped = (side == chess.BLACK)
    game_state = STATE_PLAYING
    maybe_make_engine_move()


def maybe_make_engine_move():
    """If it's the engine's turn, search for and play its move."""
    if game_state != STATE_PLAYING or board.is_game_over():
        return
    if board.turn == player_side:
        return
    engine_move = find_best_move(ENGINE_SEARCH_DEPTH, board.turn)
    if engine_move is not None:
        push_move_with_sound(board, engine_move)


def main():
    global dragging, drag_square, drag_piece
    global game_state
    running = True

    while running:
        clock.tick(60)

        if game_state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if MENU_PLAY_WHITE_RECT.collidepoint(event.pos):
                        start_game_as(chess.WHITE)
                    elif MENU_PLAY_BLACK_RECT.collidepoint(event.pos):
                        start_game_as(chess.BLACK)

            draw_menu(screen)
            pygame.display.flip()
            continue

        game_over_message = gameOverCheck(board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over_message and RESET_BUTTON_RECT.collidepoint(pygame.mouse.get_pos()):
                    reset_game()
                    continue
                elif event.button == 1 and not game_over_message and board.turn == player_side:
                    square = square_from_pos(event.pos)
                    piece = board.piece_at(square) if square is not None else None
                    if piece is not None and piece.color == player_side:
                        dragging = True
                        drag_square = square
                        drag_piece = piece.symbol()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    target_square = square_from_pos(event.pos)
                    if target_square is not None and target_square != drag_square:
                        move = chess.Move(drag_square, target_square)
                        if move not in board.legal_moves:
                            move = chess.Move(
                                drag_square, target_square, promotion=chess.QUEEN)
                        if move in board.legal_moves:
                            push_move_with_sound(board, move)
                            maybe_make_engine_move()
                        else:
                            print("illegal move, try again")
                    dragging = False
                    drag_square = None
                    drag_piece = None

        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, CARD_COLOR, APP_CARD_RECT, border_radius=CARD_RADIUS)
        drawBoard(screen)

        get_square_under_mouse(screen)
        draw_pieces_from_fen(screen, board.fen(), skip_square=drag_square)
        draw_check_indicator(screen, board)
        if dragging and drag_piece is not None:
            piece_img = piece_images[drag_piece]
            mouse_pos = pygame.mouse.get_pos()
            img_rect = piece_img.get_rect(center=mouse_pos)
            screen.blit(piece_img, img_rect)

        draw_eval_bar(screen, board)

        mouse_pos = pygame.mouse.get_pos()

        # Status row: turn indicator normally, game-over message + reset button once it ends
        if game_over_message:
            pygame.draw.rect(screen, DANGER_COLOR, GAME_STATUS_RECT, border_radius=BUTTON_RADIUS)
            draw_text_centered(screen, game_over_message, small_font, WHITE, GAME_STATUS_RECT.center)
            draw_button(screen, RESET_BUTTON_RECT, "Reset", font, TEXT_PRIMARY, ACCENT_COLOR,
                        hovered=RESET_BUTTON_RECT.collidepoint(mouse_pos))
        else:
            turn_text = f"{'White' if board.turn else 'Black'} to move"
            draw_text_left(screen, turn_text, small_font, TEXT_MUTED, GAME_STATUS_RECT, padding=4)

        pygame.display.flip()


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
                    x, y = screen_pos_for_square(square)
                    screen.blit(piece, (x, y))
                col_index += 1


def draw_check_indicator(screen, board):
    """Soft glowing ring around the king's square when its side is in check."""
    if not board.is_check():
        return
    king_square = board.king(board.turn)
    if king_square is None:
        return
    x, y = screen_pos_for_square(king_square)
    center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)

    glow = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    glow_center = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)
    pygame.draw.circle(glow, DANGER_COLOR + (70,), glow_center, SQUARE_SIZE // 2)
    screen.blit(glow, (x, y))
    pygame.draw.circle(screen, DANGER_COLOR, center, SQUARE_SIZE // 2 - 2, 4)


def draw_text_centered(surface, text, font, color, center_pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    surface.blit(text_surface, text_rect)


def draw_text_left(surface, text, font, color, rect, padding=12):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midleft=(rect.left + padding, rect.centery))
    surface.blit(text_surface, text_rect)


def draw_button(surface, rect, text, font, text_color, bg_color, hovered=False):
    color = ACCENT_HOVER_COLOR if hovered and bg_color == ACCENT_COLOR else bg_color
    pygame.draw.rect(surface, color, rect, border_radius=BUTTON_RADIUS)
    draw_text_centered(surface, text, font, text_color, rect.center)


def draw_icon_button(surface, rect, text, icon, hovered=False):
    color = INSET_COLOR if not hovered else BORDER_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(surface, BORDER_COLOR, rect, width=1, border_radius=BUTTON_RADIUS)

    icon_rect = icon.get_rect(midleft=(rect.left + 20, rect.centery))
    surface.blit(icon, icon_rect)

    text_surface = font.render(text, True, TEXT_PRIMARY)
    text_rect = text_surface.get_rect(midleft=(icon_rect.right + 16, rect.centery))
    surface.blit(text_surface, text_rect)


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
                BOARD_ORIGIN[0] + col * SQUARE_SIZE, BOARD_ORIGIN[1] + row * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE))


def get_square_under_mouse(screen):
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    for row in range(8):
        for col in range(8):
            square_rect = pygame.Rect(
                BOARD_ORIGIN[0] + col * SQUARE_SIZE, BOARD_ORIGIN[1] + row * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE)
            if square_rect.collidepoint(mouse_pos):
                inset_rect = square_rect.inflate(-8, -8)
                pygame.draw.rect(screen, ACCENT_COLOR, inset_rect, width=3, border_radius=6)


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
    global dragging, drag_square, drag_piece
    board.reset()
    dragging = False
    drag_square = None
    drag_piece = None

iterations = 0
PST_1 = {
        chess.PAWN: 
       [0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
        ],
        chess.BISHOP: 
        [-20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
        ],
        chess.KNIGHT:
        [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
        ],
        chess.ROOK:
        [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
        ],
        chess.QUEEN:
        [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
        ],
        chess.KING:
        [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
        ]


    
}

PST_2 = {
    chess.KING:
    [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
    ]
}

WHITE_TURN= True
BLACK_TURN = False
#simple evaluation based on pieces remaining on the board
def evaluate():
    white = 0
    black = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece == None:
            continue
        elif piece.color == True:
            white+= pieceValues[piece.piece_type]
            current = PST_1[piece.piece_type]
            white += current[square ^ 56]
        else:
            black+=pieceValues[piece.piece_type]
            current = PST_1[piece.piece_type]
            black += current[square]

    return white-black

def piece_advantage():
    white = 0
    black = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece == None:
            continue
        elif piece.color == True:
            white+= pieceValues[piece.piece_type]
        else:
            black+=pieceValues[piece.piece_type]
            
    
    return white-black

#basic min max function that should return the best score
#wrapper to find best move 
def engine(depth, maximizing_player):
    return engine_wrap(depth,maximizing_player, float('-inf'),float('inf'))


def engine_wrap(depth,maximizing_player,alpha, beta):
    global iterations
    iterations+=1
    if depth == 0:
        return evaluate()
    if not board.legal_moves:
        return evaluate()
    
    if maximizing_player:
        #player = true means white is to move, false means black

        best_score = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            score = engine_wrap(depth-1, BLACK_TURN, alpha, beta)
            board.pop()
            best_score = max(best_score, score)
            alpha = max(best_score, alpha)
            if alpha >= beta:
                break
        return best_score

    else:
        best_score = float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = engine_wrap(depth-1, WHITE_TURN, alpha, beta)
            board.pop()
            best_score = min(best_score, score)
            beta = min(best_score, beta)
            if beta <= alpha:
                break
        return best_score

def find_best_move(depth, player):
    #player = true means white is to move, false means black
    if board.is_game_over():
        return None
    
    if player:
        best_score = float('-inf')
        best_move = None #start at bare minimum
        for move in board.legal_moves:
            board.push(move)
            attempt = engine(depth-1,False) 
            board.pop()
            if attempt > best_score:
                best_score = attempt
                best_move = move
        return best_move
    else:
        best_score = float('inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            attempt = engine(depth-1,True)
            board.pop()
            if attempt < best_score:
                best_score = attempt
                best_move = move
        return best_move
main()
