"""
Tic Tac Toe Player
"""
import math

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    #In the initial game state, X gets the first move. 
      #Subsequently, the player alternates with each additional move.
    #Any return value is acceptable if a terminal board is provided as input 
      #(i.e., the game is already over).
    
    # Count the number of X's and O's on the board
    count_X = sum(row.count(X) for row in board)
    count_O = sum(row.count(O) for row in board)
    # If the number of X's is equal to or greater than the number of O's, it's O's turn
    if count_X <= count_O: #由於X先手，所以X的數量一定比O多，所以這裡其實用==也可以
        return X
    else:
        return O
    # raise NotImplementedError

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()  #把目前的棋盤上可以下的位置(empty)存起來
    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                possible_actions.add((i, j)) 
    return possible_actions
    # raise NotImplementedError

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #把action的位置填上目前的board，標上目前的player
    i, j = action
    # If action is not a valid action for the board, your program should raise an exception.
    if board[i][j] is not EMPTY:
        raise NotImplementedError
    new_board = [row.copy() for row in board] #複製一份board
    new_board[i][j] = player(board) #把action的位置填上目前的player
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if all(cell == row[0] for cell in row) and row[0] is not EMPTY:
            return row[0]
    
    # Check columns
    for j in range(3):
        if all(board[i][j] == board[0][j] for i in range(3)) and board[0][j] is not EMPTY:
            return board[0][j]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]
    # If there is no winner, the function should return None.
    return None
    
    # raise NotImplementedError #?用意是要raise什麼error? 目前沒想到 

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or all(all(cell is not EMPTY for cell in row) for row in board)

    # raise NotImplementedError

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winner_player = winner(board)
    if winner_player == X:
        return 1
    elif winner_player == O:
        return -1
    else:    #這應該是當遊戲結束時才會呼叫這個function吧!? 所以如果不是X或O贏，就是平手
        return 0
    # raise NotImplementedError



def minimax(board):  #這個function是用來找出最佳的action，對我來說是最難的一個function，看不太懂
    """
    Returns the optimal action for the current player on the board.
    """
    def max_value(board):  #當是X的回合時，找出最大的v
        if terminal(board):
            return utility(board)
        v = float("-inf") #v是用來存放目前最大的值，初始值為負無窮
        for action in actions(board):  #對於目前board可以下的各種actions，找出能讓結果最大的action(利於X)
            v = max(v, min_value(result(board, action)))
        return v
    
    def min_value(board):  #當是O的回合時，找出最小的v(與上面的max_value相反效果)
        if terminal(board):
            return utility(board)
        v = float("inf")
        for action in actions(board):
            v = min(v, max_value(result(board, action)))
        return v
    
    if terminal(board): #如果遊戲已經結束，就不用再找action了
        return None
    
    if player(board) == X: #如果是X的回合，就要找出最大的v
        v = float("-inf")
        best_action = None
        for action in actions(board):
            cur_value = min_value(result(board, action)) #cur_value表示此action下去後，對手O可達到的最小值
            if cur_value > v:  #如果此action下去後，對手O可達到的最小值比目前的v還大，表示此action是更有利於X，於是更新v和best_action(動態)
                v = cur_value
                best_action = action
    else:
        v = float("inf")
        best_action = None
        for action in actions(board):
            cur_value = max_value(result(board, action))
            if cur_value < v:
                v = cur_value
                best_action = action
    
    return best_action
    # raise NotImplementedError
