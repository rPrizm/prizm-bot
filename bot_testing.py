import chess

board = chess.Board()

pieceValues = {chess.PAWN: 1, chess.BISHOP: 3, chess.KNIGHT: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 9999}
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
print(board)
while True:
    if board.is_game_over():
        break
    white_move = find_best_move(5,True)
    board.push(white_move)
    print()
    print("white moves " + str(white_move))
    print(board)
    print("piece diff: "+ str(piece_advantage()))
    print("eval: "+ str(evaluate()))
    print("iterations: "+str(iterations))
    iterations = 0


    if board.is_game_over():
        break
    black_move = find_best_move(5,False)
    board.push(black_move)
    print()
    print("black moves " + str(black_move))
    print(board)
    print("piece diff: "+ str(piece_advantage()))
    print("eval: "+ str(evaluate()))
    print("iterations: "+str(iterations))
    iterations = 0


print()
print("game over:", board.outcome())




        


    
    

#actual code


