class GameState():
    def __init__(self):

        # 8*8 2D list
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getNightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # enpassant capture is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]


    #takes a move as a parameter and executes it ( castling and enpassant wont work atm)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        #update kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion 
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q' 

        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing pawn

            #update enpassantPossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingSide Castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the ks rook
                self.board[move.endRow][move.endCol+1] = "--"
            else: #queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves the qs rook
                self.board[move.endRow][move.endCol-2] = "--"
        # update castling rights - whenever its a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))


        


    #undo the last move
    def undo(self):
        if len(self.moveLog) != 0: #makes sure theres a move to do
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update kings position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" #landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            #2 square pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()


            #undo castling rights
            self.castleRightsLog.pop() #get rid of the new castle rights
            self.currentCastlingRights  = self.castleRightsLog[-1] #set the current castle rights to the last one in the list
            
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"


    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # leftrook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False   
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # leftrook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        #generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) #if they attack your king its not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undo()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                print("CheckMate!!")
            else:
                self.staleMate = True
                print("StaleMate!!")
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves 

    def inCheck(self): # this is fine
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove #switching turns to check opponents moves
        oppMoves = self.getAllPossibleMoves()
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: #square is under attack
                self.whiteToMove = not self.whiteToMove
                return True
        self.whiteToMove = not self.whiteToMove
        return False


    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)): #number of rows
            for col in range(len(self.board[row])): #number of columns in given row
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)

        return moves
            


    #get all pawn moves for the pawn

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:
            if self.board[row - 1][col] == "--": #move to the first square
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--": #move to the second square
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col-1 >= 0: #captures to the left
                if self.board[row-1][col-1][0] == 'b': #black piece to capture
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True))

            if col+1 <= 7:
                if self.board[row-1][col+1][0] == 'b': #black piece to capture
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True))

        else: #black pawn moves
            if not self.whiteToMove:
                if self.board[row + 1][col] == "--": #move to the first square
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board)) #move to the second square
                if col-1 >= 0: #captures to the left
                    if self.board[row+1][col-1][0] == 'w': #white piece to capture
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                    elif (row + 1, col - 1) == self.enpassantPossible:
                        moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True))
                if col+1 <= 7:
                    if self.board[row+1][col+1][0] == 'w': #white piece to capture
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                    elif (row + 1, col + 1) == self.enpassantPossible:
                        moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove=True))

           
    #get all rook moves for the rook
    def getRookMoves(self, row, col, moves):
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # UP, LEFT, DOWN, RIGHT
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else: # friendly piece inavalid
                        break
                else: # off board
                    break


    
    #get all knight moves
    def getNightMoves(self, row, col, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        if self.whiteToMove:
            myColor = "w"
        else:
            myColor = "b"
        for move in knightMoves:
            endRow = row + move[0]
            endCol = col + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != myColor: #make sure not moving an enemy piece
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    


    #get all bishop moves
    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # UP, LEFT, DOWN, RIGHT
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else: # friendly piece inavalid
                        break
                else: # off board
                    break

    #queen moves
    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)



    #king moves
    def getKingMoves(self, row, col, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        if self.whiteToMove:
            myColor = "w"
        else:
            myColor = "b"
        for move in kingMoves:
            endRow = row + move[0]
            endCol = col + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != myColor:
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    #castle king moves
    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return # cant castle while in check 
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, isCastleMove=True))


    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--":
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, startSQ, endSQ, board, isEnpassantMove = False, isCastleMove=False):
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
    
        #enpassant 
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        #castle move
        self.isCastleMove = isCastleMove

        #moveID
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

 

        

    #Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]