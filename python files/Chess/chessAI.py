import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2 # controls how many moves ahead findMoveMinMax function looks

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)] # returns number between first and second input

#def findBestMoveMinMaxNoRecursion(gs, validMoves):
#    turnMultiplier = 1 if gs.whiteTurn else -1
#    opponentMinMaxScore = CHECKMATE
#    bestPlayerMove = None
#    random.shuffle(validMoves)
#    for playerMove in validMoves:
#        # getting opponent's best move
#        gs.makeMove(playerMove)
#        opponentsMoves = gs.getValidMoves()
#        if gs.staleMate:
#            opponentMaxScore = STALEMATE
#        elif gs.checkMate:
#            opponentMaxScore = -CHECKMATE
#        else:
#            opponentMaxScore = -CHECKMATE
#            for opponentMove in opponentsMoves:
#                gs.makeMove(opponentMove)
#                gs.getValidMoves()
#                if gs.checkMate:
#                    score = CHECKMATE
#                elif gs.staleMate:
#                    score = STALEMATE
#                else:
#                    score = -turnMultiplier * scoreMaterial(gs.board)
#                if score > opponentMaxScore:
#                    opponentMaxScore = score
#                gs.undo()
               
    # minimization part: my new best move is minimization of opponent's score
#        if opponentMaxScore < opponentMinMaxScore:
#            opponentMinMaxScore = opponentMaxScore
#            bestPlayerMove = playerMove
#        gs.undo()
#    return bestPlayerMove

# helper function for findMoveMinMax (to make first recursive call)
def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteTurn)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteTurn else -1)

    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteTurn):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteTurn:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-2, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo()
        return minScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    # move ordering - implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undo()
        if maxScore > alpha: # pruning phase
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

# more advanced way of scoring board
# a positive score is good for white, negative score good for black
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteTurn:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.staleMate:
        return STALEMATE
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score

# score the board based on material
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score