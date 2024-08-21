import pygame
import chess

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (109, 79, 75)
LIGHT_BROWN = (237, 201, 175)
SQUARE_SIZE = 60

#load images into variables 

bB = pygame.image.load("media/black_bishop.png")
bK = pygame.image.load("media/black_king.png")
bN = pygame.image.load("media/black_knight.png")
bP = pygame.image.load("media/black_pawn.png")
bQ = pygame.image.load("media/black_queen.png")
bR = pygame.image.load("media/black_rook.png")
wB = pygame.image.load("media/white_bishop.png")
wK = pygame.image.load("media/white_king.png")
wN = pygame.image.load("media/white_knight.png")
wP = pygame.image.load("media/white_pawn.png")
wQ = pygame.image.load("media/white_queen.png")
wr = pygame.image.load("media/white_rook.png")


# pygame setup
pygame.init()
screen = pygame.display.set_mode((480, 480))
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
        
        pygame.display.flip()


def drawBoard(screen):
    #Draws an 8x8 chessboard using alternating colors.
    for row in range(8):
        for col in range(8):
            # Alternate between two colors
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def drawPieces(screen):
    pass


main()
