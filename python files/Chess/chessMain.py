# handles user input and displays current gameState object

import pygame as p
import chessEngine, chessAI

width = height = 512 # used for the chess pieces
dimension = 8 # dimensions of the chess board
squareSize = height//dimension
maxFPS = 15
images = {}

# loading in the images (called only once)
def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR', 'wP']
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("Chess/pieceImages/" + piece + ".png"), (squareSize, squareSize))


# main will handle user input and updating graphics
def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.gameState()
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made
    animate = False # flag variable for when we should animate a move

    loadImages()
    running = True
    sqSelected = () # keeps track of last click of the user (tuple: (row, col))
    playerClicks = [] # keep track of player clicks (2 tuples: [(6,4), (4,4)])
    gameOver = False
    playerOne = True # if human playing white, this is true, if ai playing then false
    playerTwo = False # same as above but for black

    while running:
        humanTurn = (gs.whiteTurn and playerOne) or (not gs.whiteTurn and playerTwo)
        for e in p.event.get():
            # just for quitting the game
            if e.type == p.QUIT:
                running = False

            # for mouse click events
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # location of mouse
                    col = location[0]//squareSize
                    row = location[1]//squareSize
                    if sqSelected == (row, col): # if user clicks same square twice (undo action)
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # append for both first and second clicks
                    
                    if len(playerClicks) == 2: # after 2nd click
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u: # undo when 'u' is pressed
                    gs.undo()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r: # reset board when 'r' is pressed
                    gs = chessEngine.gameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
        
        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = chessAI.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = chessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteTurn:
                drawText(screen, 'black wins by checkmate')
            else:
                drawText(screen, 'white wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'stalemate')

        clock.tick(maxFPS)
        p.display.flip()

# highlight square selected and moves for piece selected
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteTurn else 'b'): # sqSelected is a piece that can be moved
            # highlighting selected square
            s = p.Surface((squareSize,squareSize))
            s.set_alpha(100) # transparancy value (0 transparent, 255 opaque)
            s.fill(p.Color('green'))
            screen.blit(s, (c*squareSize, r*squareSize))
           
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*squareSize, move.endRow*squareSize))
            
            # highlight king in red if in check
            if gs.inCheck():
                s.fill(p.Color('red'))
                screen.blit(s, (gs.whiteKingLocation[1]*squareSize, gs.whiteKingLocation[0]*squareSize))

# handles all graphics within current game state
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # draw pieces on top of squares

def drawBoard(screen):
    global colors
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*squareSize, r*squareSize, squareSize, squareSize))

def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]

            if piece != "--":
                screen.blit(images[piece], p.Rect(c*squareSize, r*squareSize, squareSize, squareSize))

# animating a move
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow # change in row
    dC = move.endCol - move.startCol # change in column
    framesPerSquare = 10 # frames to move one sqaure
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)

        # erase piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*squareSize, move.endRow*squareSize, squareSize, squareSize)
        p.draw.rect(screen, color, endSquare)

        # draw the captured piece onto the rectangle
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured], endSquare)
        
        # draw moving piece
        screen.blit(images[move.pieceMoved], p.Rect(c*squareSize, r*squareSize, squareSize, squareSize))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitica", 32, True, False)
    textObject = font.render(text, 0, p.Color('gray'))
    textLocation = p.Rect(0, 0, width, height).move(width/2 - textObject.get_width()/2, height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('black'))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()





