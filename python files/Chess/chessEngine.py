# stores all info on current game state
# determines valid and invalid moves

class gameState():
    def __init__(self):
        # the board is an 8 by 8 two dimensional list
        # "--" means blank space with no piece on it
        # this is what the starting gameboard will look like
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP","bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP","wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteTurn = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # coordinates for square where enpassant capture is possible
        self.currentCastlingRight = castleRights(True, True, True, True)
        self.castleRightsLog = [castleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log move so we can undo later
        self.whiteTurn = not self.whiteTurn # switch player turns
        
        # update king location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # capturing the pawn
        
        # update enpassantPossible variable
        if (move.pieceMoved[1] == 'P') and (abs(move.startRow - move.endRow) == 2): # only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # king side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # moves the rook
                self.board[move.endRow][move.endCol+1] = '--' # erase old rook
            else: # queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # moves the rook
                self.board[move.endRow][move.endCol-2] = '--'

        # updating castling rights (whenever rook or king moves)
        self.updateCastleRights(move)
        self.castleRightsLog.append(castleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    # undoes the last move (recorded in the movelog)
    def undo(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteTurn = not self.whiteTurn
            # update king location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            
            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            
            # undo a 2 square pawn advance
            if (move.pieceMoved[1] == 'P') and (abs(move.startRow - move.endRow) == 2):
                self.enpassantPossible = ()
            
            # undo castling rights
            self.castleRightsLog.pop() # get rid of new castle rights from move we are undoing
            newRights = self.castleRightsLog[-1] # set current castle rights to last one in the list
            self.currentCastlingRight = castleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # king side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: # queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            
            self.checkMate = False
            self.staleMate = False
    
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.bks = False

    # all moves that are checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        # copy current castling rights
        tempCastleRights = castleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteTurn:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves)-1, -1, -1): # when removing from list, go backwards
            self.makeMove(moves[i])
            self.whiteTurn = not self.whiteTurn
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteTurn = not self.whiteTurn
            self.undo()
            
        # check to see if either checkmate or stalemate
        if len(moves) == 0: 
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves
    
    # determine if current player in check
    def inCheck(self):
        if self.whiteTurn:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # determine if enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteTurn = not self.whiteTurn # switch to opponent turn
        opponentMoves = self.getAllPossibleMoves()
        self.whiteTurn = not self.whiteTurn # switch turns back
        for move in opponentMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                return True
        return False

    # all moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of cols in a row
                pieceColor = self.board[r][c][0]
                if(pieceColor == 'w' and self.whiteTurn) or (pieceColor == 'b' and not self.whiteTurn):
                    pieceModel = self.board[r][c][1]

                    if pieceModel == 'P': # if the piece model is pawn
                        self.getPawnMoves(r,c,moves)

                    elif pieceModel == 'R': # if piece model is rook
                        self.getRookMoves(r,c,moves)
                    
                    elif pieceModel == 'N': # if piece model is knight
                        self.getKnightMoves(r,c,moves)
                    
                    elif pieceModel == 'B': # if piece model is bishop
                        self.getBishopMoves(r,c,moves)
                        
                    elif pieceModel == 'Q': # if piece model is Queen
                        self.getQueenMoves(r,c,moves)
                    
                    elif pieceModel == 'K': # if piece model is King
                        self.getKingMoves(r,c,moves)
        return moves

    # for all "get" moves, gets all moves for the piece located at row, col and adds these moves to a list
    def getPawnMoves(self, r, c, moves):
        # for white pawn
        if self.whiteTurn: 
            if self.board[r-1][c] == "--": # one square advance
                moves.append(Move((r,c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": # two square advance
                    moves.append(Move((r,c), (r-2,c), self.board))
            
            # for captures (diagonal moves)
            if c-1 >= 0: # capture to the left
                if self.board[r-1][c-1][0] == 'b': 
                    moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7: # capture to the right      
                if self.board[r-1][c+1][0] == 'b': 
                    moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c+1), self.board, isEnpassantMove=True))
       
        # black pawn moves
        else:
            if self.board[r+1][c] == "--": # one square advance
                moves.append(Move((r,c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": # two square advance
                    moves.append(Move((r,c), (r+2,c), self.board))
            
             # for captures (diagonal moves)
            if c-1 >= 0: # capture to the left
                if self.board[r+1][c-1][0] == 'w': 
                    moves.append(Move((r,c), (r+1,c-1), self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1,c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7: # capture to the right      
                if self.board[r+1][c+1][0] == 'w': 
                    moves.append(Move((r,c), (r+1,c+1), self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1,c+1), self.board, isEnpassantMove=True))


    def getRookMoves(self, r, c, moves):
        # for white rook
        if self.whiteTurn:
            row = 1
            col = 1
            finished = False
            up = True
            down = True
            right = True
            left = True
        
            # incrementing rows and columns
            while finished == False:
                # check rows down
                if r+row < len(self.board):
                    if (self.board[r+row][c][0] == 'w') and (down == True):
                        down = False
                    if (self.board[r+row][c][0] == 'b') and (down == True):
                        moves.append(Move((r,c), (r+row,c), self.board))
                        down = False
                    if down == True:
                        moves.append(Move((r,c), (r+row,c), self.board))

                # check columns to the right   
                if c+col < len(self.board):
                    if (self.board[r][c+col][0] == 'w') and (right == True):
                        right = False
                    if (self.board[r][c+col][0] == 'b') and (right == True):
                        moves.append(Move((r,c), (r,c+col), self.board))
                        right = False
                    if right == True:
                        moves.append(Move((r,c), (r,c+col), self.board))
                
                # check rows up
                if r-row >= 0:
                    if (self.board[r-row][c][0] == 'w') and (up == True):
                        up = False
                    if (self.board[r-row][c][0] == 'b') and (up == True):
                        moves.append(Move((r,c), (r-row,c), self.board))
                        up = False
                    if up == True:
                        moves.append(Move((r,c), (r-row,c), self.board))

                # check columns to the left   
                if c-col >= 0:
                    if (self.board[r][c-col][0] == 'w') and (left == True):
                        left = False
                    if (self.board[r][c-col][0] == 'b') and (left == True):
                        moves.append(Move((r,c), (r,c-col), self.board))
                        left = False
                    if left == True:
                        moves.append(Move((r,c), (r,c-col), self.board))
                
                # incrementing variables
                row = row + 1
                col = col + 1
            
                # check if end of rows and columns
                if (r+row >= len(self.board)) and (c+col >= len(self.board)) and (r-row < 0) and (c-col < 0):
                    finished = True

        # for black rook          
        else:    
            row = 1
            col = 1
            finished = False
            up = True
            down = True
            right = True
            left = True

            # incrementing rows and columns
            while finished == False:
                # check rows down
                if r+row < len(self.board):
                    if (self.board[r+row][c][0] == 'b') and (down == True):
                        down = False
                    if (self.board[r+row][c][0] == 'w') and (down == True):
                        moves.append(Move((r,c), (r+row,c), self.board))
                        down = False
                    if down == True:
                        moves.append(Move((r,c), (r+row,c), self.board))

                # check columns to the right   
                if c+col < len(self.board):
                    if (self.board[r][c+col][0] == 'b') and (right == True):
                        right = False
                    if (self.board[r][c+col][0] == 'w') and (right == True):
                        moves.append(Move((r,c), (r,c+col), self.board))
                        right = False
                    if right == True:
                        moves.append(Move((r,c), (r,c+col), self.board))
                
                 # check rows up
                if r-row >= 0:
                    if (self.board[r-row][c][0] == 'b') and (up == True):
                        up = False
                    if (self.board[r-row][c][0] == 'w') and (up == True):
                        moves.append(Move((r,c), (r-row,c), self.board))
                        up = False
                    if up == True:
                        moves.append(Move((r,c), (r-row,c), self.board))

                # check columns to the left   
                if c-col >= 0:
                    if (self.board[r][c-col][0] == 'b') and (left == True):
                        left = False
                    if (self.board[r][c-col][0] == 'w') and (left == True):
                        moves.append(Move((r,c), (r,c-col), self.board))
                        left = False
                    if left == True:
                        moves.append(Move((r,c), (r,c-col), self.board))
                
                # incrementing variables
                row = row + 1
                col = col + 1
            
                # check if end of rows and columns
                if (r+row >= len(self.board)) and (c+col >= len(self.board)) and (r-row < 0) and (c-col < 0):
                    finished = True
    
    def getKnightMoves(self, r, c, moves):
        # for white knight
        if self.whiteTurn:
            # check down 1 right 2
            if (r+1 < len(self.board)) and (c+2 < len(self.board)):
                if (self.board[r+1][c+2][0] == 'b') or (self.board[r+1][c+2][0] == '-'):
                    moves.append(Move((r,c), (r+1,c+2), self.board))
            
            # check down 1 left 2
            if (r+1 < len(self.board)) and (c-2 >= 0):
                if (self.board[r+1][c-2][0] == 'b') or (self.board[r+1][c-2][0] == '-'):
                    moves.append(Move((r,c), (r+1,c-2), self.board))
            
            # check down 2 right 1
            if (r+2 < len(self.board)) and (c+1 < len(self.board)):
                if (self.board[r+2][c+1][0] == 'b') or (self.board[r+2][c+1][0] == '-'):
                    moves.append(Move((r,c), (r+2,c+1), self.board))
            
            # check down 2 left 1
            if (r+2 < len(self.board)) and (c-1 >= 0):
                if (self.board[r+2][c-1][0] == 'b') or (self.board[r+2][c-1][0] == '-'):
                    moves.append(Move((r,c), (r+2,c-1), self.board))
            
            # check up 1 right 2
            if (r-1 >= 0) and (c+2 < len(self.board)):
                if (self.board[r-1][c+2][0] == 'b') or (self.board[r-1][c+2][0] == '-'):
                    moves.append(Move((r,c), (r-1,c+2), self.board))
            
            # check up 1 left 2
            if (r-1 >= 0) and (c-2 >= 0):
                if (self.board[r-1][c-2][0] == 'b') or (self.board[r-1][c-2][0] == '-'):
                    moves.append(Move((r,c), (r-1,c-2), self.board))
            
            # check up 2 right 1
            if (r-2 >= 0) and (c+1 < len(self.board)):
                if (self.board[r-2][c+1][0] == 'b') or (self.board[r-2][c+1][0] == '-'):
                    moves.append(Move((r,c), (r-2,c+1), self.board))
            
            # check up 2 left 1
            if (r-2 >= 0) and (c-1 >= 0):
                if (self.board[r-2][c-1][0] == 'b') or (self.board[r-2][c-1][0] == '-'):
                    moves.append(Move((r,c), (r-2,c-1), self.board))

        # for black knight
        else:
            # check down 1 right 2
            if (r+1 < len(self.board)) and (c+2 < len(self.board)):
                if (self.board[r+1][c+2][0] == 'w') or (self.board[r+1][c+2][0] == '-'):
                    moves.append(Move((r,c), (r+1,c+2), self.board))
            
            # check down 1 left 2
            if (r+1 < len(self.board)) and (c-2 >= 0):
                if (self.board[r+1][c-2][0] == 'w') or (self.board[r+1][c-2][0] == '-'):
                    moves.append(Move((r,c), (r+1,c-2), self.board))
            
            # check down 2 right 1
            if (r+2 < len(self.board)) and (c+1 < len(self.board)):
                if (self.board[r+2][c+1][0] == 'w') or (self.board[r+2][c+1][0] == '-'):
                    moves.append(Move((r,c), (r+2,c+1), self.board))
            
            # check down 2 left 1
            if (r+2 < len(self.board)) and (c-1 >= 0):
                if (self.board[r+2][c-1][0] == 'w') or (self.board[r+2][c-1][0] == '-'):
                    moves.append(Move((r,c), (r+2,c-1), self.board))
            
            # check up 1 right 2
            if (r-1 >= 0) and (c+2 < len(self.board)):
                if (self.board[r-1][c+2][0] == 'w') or (self.board[r-1][c+2][0] == '-'):
                    moves.append(Move((r,c), (r-1,c+2), self.board))
            
            # check up 1 left 2
            if (r-1 >= 0) and (c-2 >= 0):
                if (self.board[r-1][c-2][0] == 'w') or (self.board[r-1][c-2][0] == '-'):
                    moves.append(Move((r,c), (r-1,c-2), self.board))
            
            # check up 2 right 1
            if (r-2 >= 0) and (c+1 < len(self.board)):
                if (self.board[r-2][c+1][0] == 'w') or (self.board[r-2][c+1][0] == '-'):
                    moves.append(Move((r,c), (r-2,c+1), self.board))
            
            # check up 2 left 1
            if (r-2 >= 0) and (c-1 >= 0):
                if (self.board[r-2][c-1][0] == 'w') or (self.board[r-2][c-1][0] == '-'):
                    moves.append(Move((r,c), (r-2,c-1), self.board))

    def getBishopMoves(self, r, c, moves):
        # for white bishop
        if self.whiteTurn:
            row = 1
            col = 1
            finished = False
            upRight = True
            downRight = True
            upLeft = True
            downLeft = True
        
            # incrementing rows and columns
            while finished == False:
                # check up and to the right
                if (r-row >= 0) and (c+col < len(self.board)):
                    if (self.board[r-row][c+col][0] == 'w') and (upRight == True):
                        upRight = False
                    if (self.board[r-row][c+col][0] == 'b') and (upRight == True):
                        moves.append(Move((r,c), (r-row,c+col), self.board))
                        upRight = False
                    if upRight == True:
                        moves.append(Move((r,c), (r-row,c+col), self.board))

                # check up and to the left
                if (r-row >= 0) and (c-col >= 0):
                    if (self.board[r-row][c-col][0] == 'w') and (upLeft == True):
                        upLeft = False
                    if (self.board[r-row][c-col][0] == 'b') and (upLeft == True):
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                        upLeft = False
                    if upLeft == True:
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                
                # check down and to the left
                if (r+row < len(self.board)) and (c-col >= 0):
                    if (self.board[r+row][c-col][0] == 'w') and (downLeft == True):
                        downLeft = False
                    if (self.board[r+row][c-col][0] == 'b') and (downLeft == True):
                        moves.append(Move((r,c), (r+row,c-col), self.board))
                        downLeft = False
                    if downLeft == True:
                        moves.append(Move((r,c), (r+row,c-col), self.board))
                
                # check down and to the right
                if (r+row < len(self.board)) and (c+col < len(self.board)):
                    if (self.board[r+row][c+col][0] == 'w') and (downRight == True):
                        downRight = False
                    if (self.board[r+row][c+col][0] == 'b') and (downRight == True):
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                        downRight = False
                    if downRight == True:
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                
                # incrementing variables
                row = row + 1
                col = col + 1

                # check if end of rows and columns
                if (r-row < 0) and (c-col < 0) and (r+row >= len(self.board)) and (c+col >= len(self.board)):
                    finished = True
        
        # for black bishop           
        else:
            row = 1
            col = 1
            finished = False
            upRight = True
            downRight = True
            upLeft = True
            downLeft = True
        
            # incrementing rows and columns
            while finished == False:
                # check up and to the right
                if (r-row >= 0) and (c+col < len(self.board)):
                    if (self.board[r-row][c+col][0] == 'b') and (upRight == True):
                        upRight = False
                    if (self.board[r-row][c+col][0] == 'w') and (upRight == True):
                        moves.append(Move((r,c), (r-row,c+col), self.board))
                        upRight = False
                    if upRight == True:
                        moves.append(Move((r,c), (r-row,c+col), self.board))

                # check up and to the left
                if (r-row >= 0) and (c-col >= 0):
                    if (self.board[r-row][c-col][0] == 'b') and (upLeft == True):
                        upLeft = False
                    if (self.board[r-row][c-col][0] == 'w') and (upLeft == True):
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                        upLeft = False
                    if upLeft == True:
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                
                # check down and to the left
                if (r+row < len(self.board)) and (c-col >= 0):
                    if (self.board[r+row][c-col][0] == 'b') and (downLeft == True):
                        downLeft = False
                    if (self.board[r+row][c-col][0] == 'w') and (downLeft == True):
                        moves.append(Move((r,c), (r+row,c-col), self.board))
                        downLeft = False
                    if downLeft == True:
                        moves.append(Move((r,c), (r+row,c-col), self.board))
                
                # check down and to the right
                if (r+row < len(self.board)) and (c+col < len(self.board)):
                    if (self.board[r+row][c+col][0] == 'b') and (downRight == True):
                        downRight = False
                    if (self.board[r+row][c+col][0] == 'w') and (downRight == True):
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                        downRight = False
                    if downRight == True:
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                
                # incrementing variables
                row = row + 1
                col = col + 1

                # check if end of rows and columns
                if (r-row < 0) and (c-col < 0) and (r+row >= len(self.board)) and (c+col >= len(self.board)):
                    finished = True

    def getQueenMoves(self, r, c, moves):
        # for white queen
        if self.whiteTurn:
            row = 1
            col = 1
            finished = False
            up = True
            upRight = True
            right = True
            downRight = True
            down = True
            upLeft = True
            left = True
            downLeft = True

            while finished == False:
                # down
                if (r+row < len(self.board)):
                    if (self.board[r+row][c][0] == 'w') and (down == True):
                        down = False
                    if (self.board[r+row][c][0] == 'b') and (down == True):
                        moves.append(Move((r,c), (r+row,c), self.board))
                        down = False
                    if down == True:
                        moves.append(Move((r,c), (r+row,c), self.board))
            
                # down and right
                if (r+row < len(self.board)) and (c+col < len(self.board)):
                    if (self.board[r+row][c+col][0] == 'w') and (downRight == True):
                        downRight = False
                    if (self.board[r+row][c+col][0] == 'b') and (downRight == True):
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                        downRight = False
                    if downRight == True:
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                
                # right
                if c+col < len(self.board):
                    if (self.board[r][c+col][0] == 'w') and (right == True):
                        right = False
                    if (self.board[r][c+col][0] == 'b') and (right == True):
                        moves.append(Move((r,c), (r,c+col), self.board))
                        right = False
                    if right == True:
                        moves.append(Move((r,c), (r,c+col), self.board))
                
                # up and right
                if (r-row >= 0) and (c+col < len(self.board)):
                    if (self.board[r-row][c+col][0] == 'w') and (upRight == True):
                        upRight = False
                    if (self.board[r-row][c+col][0] == 'b') and (upRight == True):
                        moves.append(Move((r,c), (r-row,c+col), self.board))
                        upRight = False
                    if upRight == True:
                        moves.append(Move((r,c), (r-row,c+col), self.board))
                
                # up
                if r-row >= 0:
                    if (self.board[r-row][c][0] == 'w') and (up == True):
                        up = False
                    if (self.board[r-row][c][0] == 'b') and (up == True):
                        moves.append(Move((r,c), (r-row,c), self.board))
                        up = False
                    if up == True:
                        moves.append(Move((r,c), (r-row,c), self.board))
                
                # up and left
                if (r-row >= 0) and (c-col >= 0):
                    if (self.board[r-row][c-col][0] == 'w') and (upLeft == True):
                        upLeft = False
                    if (self.board[r-row][c-col][0] == 'b') and (upLeft == True):
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                        upLeft = False
                    if upLeft == True:
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                
                # left
                if c-col >= 0:
                    if (self.board[r][c-col][0] == 'w') and (left == True):
                        left = False
                    if (self.board[r][c-col][0] == 'b') and (left == True):
                        moves.append(Move((r,c), (r,c-col), self.board))
                        left = False
                    if left == True:
                        moves.append(Move((r,c), (r,c-col), self.board))
                
                # down and left
                if (r+row < len(self.board)) and (c-col >= 0):
                    if (self.board[r+row][c-col][0] == 'w') and (downLeft == True):
                        downLeft = False
                    if (self.board[r+row][c-col][0] == 'b') and (downLeft == True):
                        moves.append(Move((r,c), (r+row,c-col), self.board))
                        downLeft = False
                    if downLeft == True:
                        moves.append(Move((r,c), (r+row,c-col), self.board))

                # incrementing variables
                row = row + 1
                col = col + 1

                # check if end of rows and columns
                if (r+row >= len(self.board)) and (c+col >= len(self.board)) and (r-row < 0) and (c-col < 0):
                    finished = True

        # for black queen
        else:
            row = 1
            col = 1
            finished = False
            up = True
            upRight = True
            right = True
            downRight = True
            down = True
            upLeft = True
            left = True
            downLeft = True

            while finished == False:
                # down
                if (r+row < len(self.board)):
                    if (self.board[r+row][c][0] == 'b') and (down == True):
                        down = False
                    if (self.board[r+row][c][0] == 'w') and (down == True):
                        moves.append(Move((r,c), (r+row,c), self.board))
                        down = False
                    if down == True:
                        moves.append(Move((r,c), (r+row,c), self.board))
            
                # down and right
                if (r+row < len(self.board)) and (c+col < len(self.board)):
                    if (self.board[r+row][c+col][0] == 'b') and (downRight == True):
                        downRight = False
                    if (self.board[r+row][c+col][0] == 'w') and (downRight == True):
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                        downRight = False
                    if downRight == True:
                        moves.append(Move((r,c), (r+row,c+col), self.board))
                
                # right
                if c+col < len(self.board):
                    if (self.board[r][c+col][0] == 'b') and (right == True):
                        right = False
                    if (self.board[r][c+col][0] == 'w') and (right == True):
                        moves.append(Move((r,c), (r,c+col), self.board))
                        right = False
                    if right == True:
                        moves.append(Move((r,c), (r,c+col), self.board))
                
                # up and right
                if (r-row >= 0) and (c+col < len(self.board)):
                    if (self.board[r-row][c+col][0] == 'b') and (upRight == True):
                        upRight = False
                    if (self.board[r-row][c+col][0] == 'w') and (upRight == True):
                        moves.append(Move((r,c), (r-row,c+col), self.board))
                        upRight = False
                    if upRight == True:
                        moves.append(Move((r,c), (r-row,c+col), self.board))
                
                # up
                if r-row >= 0:
                    if (self.board[r-row][c][0] == 'b') and (up == True):
                        up = False
                    if (self.board[r-row][c][0] == 'w') and (up == True):
                        moves.append(Move((r,c), (r-row,c), self.board))
                        up = False
                    if up == True:
                        moves.append(Move((r,c), (r-row,c), self.board))
                
                # up and left
                if (r-row >= 0) and (c-col >= 0):
                    if (self.board[r-row][c-col][0] == 'b') and (upLeft == True):
                        upLeft = False
                    if (self.board[r-row][c-col][0] == 'w') and (upLeft == True):
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                        upLeft = False
                    if upLeft == True:
                        moves.append(Move((r,c), (r-row,c-col), self.board))
                
                # left
                if c-col >= 0:
                    if (self.board[r][c-col][0] == 'b') and (left == True):
                        left = False
                    if (self.board[r][c-col][0] == 'w') and (left == True):
                        moves.append(Move((r,c), (r,c-col), self.board))
                        left = False
                    if left == True:
                        moves.append(Move((r,c), (r,c-col), self.board))
                
                # down and left
                if (r+row < len(self.board)) and (c-col >= 0):
                    if (self.board[r+row][c-col][0] == 'b') and (downLeft == True):
                        downLeft = False
                    if (self.board[r+row][c-col][0] == 'w') and (downLeft == True):
                        moves.append(Move((r,c), (r+row,c-col), self.board))
                        downLeft = False
                    if downLeft == True:
                        moves.append(Move((r,c), (r+row,c-col), self.board))

                # incrementing variables
                row = row + 1
                col = col + 1

                # check if end of rows and columns
                if (r+row >= len(self.board)) and (c+col >= len(self.board)) and (r-row < 0) and (c-col < 0):
                    finished = True

    def getKingMoves(self, r, c, moves):
        # for white king
        if self.whiteTurn:
            # down
            if r+1 < len(self.board):
                if (self.board[r+1][c][0] == 'b') or (self.board[r+1][c][0] == '-'):
                    moves.append(Move((r,c), (r+1,c), self.board))
            
            # down and right
            if (r+1 < len(self.board)) and (c+1 < len(self.board)):
                if (self.board[r+1][c+1][0] == 'b') or (self.board[r+1][c+1][0] == '-'):
                    moves.append(Move((r,c), (r+1,c+1), self.board))
            
            # right
            if c+1 < len(self.board):
                if (self.board[r][c+1][0] == 'b') or (self.board[r][c+1][0] == '-'):
                    moves.append(Move((r,c), (r,c+1), self.board))
            
            # up and right
            if (r-1 >= 0) and (c+1 < len(self.board)):
                if (self.board[r-1][c+1][0] == 'b') or (self.board[r-1][c+1][0] == '-'):
                    moves.append(Move((r,c), (r-1,c+1), self.board))
            
            # up
            if r-1 >= 0:
                if (self.board[r-1][c][0] == 'b') or (self.board[r-1][c][0] == '-'):
                    moves.append(Move((r,c), (r-1,c), self.board))
            
            # up and left
            if (r-1 >= 0) and (c-1 >= 0):
                if (self.board[r-1][c-1][0] == 'b') or (self.board[r-1][c-1][0] == '-'):
                    moves.append(Move((r,c), (r-1,c-1), self.board))
            
            # left
            if c-1 >= 0:
                if (self.board[r][c-1][0] == 'b') or (self.board[r][c-1][0] == '-'):
                    moves.append(Move((r,c), (r,c-1), self.board))
            
            # down and left
            if (r+1 < len(self.board)) and (c-1 >= 0):
                if (self.board[r+1][c-1][0] == 'b') or (self.board[r+1][c-1][0] == '-'):
                    moves.append(Move((r,c), (r+1,c-1), self.board))
        
        # for black king
        else:
            # down
            if r+1 < len(self.board):
                if (self.board[r+1][c][0] == 'w') or (self.board[r+1][c][0] == '-'):
                    moves.append(Move((r,c), (r+1,c), self.board))
            
            # down and right
            if (r+1 < len(self.board)) and (c+1 < len(self.board)):
                if (self.board[r+1][c+1][0] == 'w') or (self.board[r+1][c+1][0] == '-'):
                    moves.append(Move((r,c), (r+1,c+1), self.board))
            
            # right
            if c+1 < len(self.board):
                if (self.board[r][c+1][0] == 'w') or (self.board[r][c+1][0] == '-'):
                    moves.append(Move((r,c), (r,c+1), self.board))
            
            # up and right
            if (r-1 >= 0) and (c+1 < len(self.board)):
                if (self.board[r-1][c+1][0] == 'w') or (self.board[r-1][c+1][0] == '-'):
                    moves.append(Move((r,c), (r-1,c+1), self.board))
            
            # up
            if r-1 >= 0:
                if (self.board[r-1][c][0] == 'w') or (self.board[r-1][c][0] == '-'):
                    moves.append(Move((r,c), (r-1,c), self.board))
            
            # up and left
            if (r-1 >= 0) and (c-1 >= 0):
                if (self.board[r-1][c-1][0] == 'w') or (self.board[r-1][c-1][0] == '-'):
                    moves.append(Move((r,c), (r-1,c-1), self.board))
            
            # left
            if c-1 >= 0:
                if (self.board[r][c-1][0] == 'w') or (self.board[r][c-1][0] == '-'):
                    moves.append(Move((r,c), (r,c-1), self.board))
            
            # down and left
            if (r+1 < len(self.board)) and (c-1 >= 0):
                if (self.board[r+1][c-1][0] == 'w') or (self.board[r+1][c-1][0] == '-'):
                    moves.append(Move((r,c), (r+1,c-1), self.board))

    # get all valid moves for king at (r,c) and add to list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r,c):
            return # cant't castle while in check
        if (self.whiteTurn and self.currentCastlingRight.wks) or (not self.whiteTurn and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteTurn and self.currentCastlingRight.wqs) or (not self.whiteTurn and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves)

    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove = True))

class castleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, startsq, endsq, board, isEnpassantMove=False, isCastleMove = False):
        self.startRow = startsq[0]
        self.startCol = startsq[1]
        self.endRow = endsq[0]
        self.endCol = endsq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False

        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        # castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]