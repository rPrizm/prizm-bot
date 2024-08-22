import pygame
import chess

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (109, 79, 75)
LIGHT_BROWN = (237, 201, 175)
SQUARE_SIZE = 60
HIGHLIGHT_COLOR = (255, 0, 0)  # Red color for the border when hovered
coordDict = {'a':0,'b':60,'c':120,'d':180,'e':240,'f':300,'g':360,'h':420}
numberDict = {'1':420,'2':360,'3':300,'4':240,'5':180,'6':120,'7':60,'8':0}

class Pieces:
    def __init__(self,image,piece,coord):
        self.image = image
        self.piece = piece
        self.coord = coord
    def convertToCoord(self):
        
        return (coordDict[self.coord[0]],numberDict[self.coord[1]])
    
#load images into variables 
#black pieces
bB1 = Pieces(pygame.image.load("media/black_bishop.png"),"bishop","c8")
bB2 = Pieces(pygame.image.load("media/black_bishop.png"),"bishop","f8")
bK = Pieces(pygame.image.load("media/black_king.png"),"king","e8")
bN1 = Pieces(pygame.image.load("media/black_knight.png"),"knight","b8")
bN2 = Pieces(pygame.image.load("media/black_knight.png"),"knight","g8")
bQ = Pieces(pygame.image.load("media/black_queen.png"),"queen","d8")
bR1 = Pieces(pygame.image.load("media/black_rook.png"),"rook","a8")
bR2 = Pieces(pygame.image.load("media/black_rook.png"),"rook","h8")
#white pieces
wB1 = Pieces(pygame.image.load("media/white_bishop.png"),"bishop","c1")
wB2 = Pieces(pygame.image.load("media/white_bishop.png"),"bishop","f1")
wK = Pieces(pygame.image.load("media/white_king.png"),"king","e1")
wN1 = Pieces(pygame.image.load("media/white_knight.png"),"knight","b1")
wN2 = Pieces(pygame.image.load("media/white_knight.png"),"knight","g1")
wQ = Pieces(pygame.image.load("media/white_queen.png"),"queen","d1")
wR1 = Pieces(pygame.image.load("media/white_rook.png"),"rook","a1")
wR2 = Pieces(pygame.image.load("media/white_rook.png"),"rook","h1")
#black pawns
bP1 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","a7")
bP2 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","b7")
bP3 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","c7")
bP4 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","d7")
bP5 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","e7")
bP6 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","f7")
bP7 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","g7")
bP8 = Pieces(pygame.image.load("media/black_pawn.png"),"pawn","h7")
#white pawns
wP1 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","a2")
wP2 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","b2")
wP3 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","c2")
wP4 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","d2")
wP5 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","e2")
wP6 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","f2")
wP7 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","g2")
wP8 = Pieces(pygame.image.load("media/white_pawn.png"),"pawn","h2")

#list with all the pieces, when a piece is removed, it will be popped off the list and no longer rendered
mainPieceList = [bB1,bB2,bK,bN1,bN2,bQ,bR1,bR2,wB1,wB2,wK,wN1,wN2,wQ,wR1,wR2,wP1,wP2,wP3,wP4,wP5,wP6,wP7,wP8,bP1,bP2,bP3,bP4,bP5,bP6,bP7,bP8]





# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_icon(pygame.image.load("media/black_knight.png"))
pygame.display.set_caption("Chess GUI")
clock = pygame.time.Clock()


def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
           
# draw elements here
        drawBoard(screen)
        printPieces(mainPieceList)
        get_square_under_mouse(screen)
        
        
        pygame.display.flip()







def drawBoard(screen):
    #Draws an 8x8 chessboard using alternating colors.
    for row in range(8):
        for col in range(8):
            # Alternate between two colors
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def printPieces(piece_list):
    for i in piece_list:
        screen.blit(i.image,i.convertToCoord())


def get_square_under_mouse(screen):
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    for row in range(8):
        for col in range(8):
            square_rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if square_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, square_rect, 3)  # Draw a red border

def make_pieces_draggable(piece_list):
    pass



main()
print(f"{wB1.convertToCoord()} {wB1.coord}")