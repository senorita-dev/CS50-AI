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
    played_count = 0
    for row in board:
        for cell in row:
            if cell != EMPTY:
                played_count += 1
        pass
    if played_count == 9:
        return None
    if played_count % 2 == 0:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = []
    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):
            if cell == EMPTY:
                possible_actions.append((row_index, col_index))
            pass
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row, col = action
    cell = board[row][col]
    if cell != EMPTY:
        raise ValueError
    
    copy_board = [list(row) for row in board]
    copy_board[row][col] = player(board)
    return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != EMPTY:
            return board[row][0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2] 
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    current_player = player(board)
    possible_actions = actions(board)
    utility_action_map = dict()
    if current_player == X:
        for action in possible_actions:
            value = min_value(result(board, action))
            utility_action_map[value] = action
            pass
        max_utility = max(utility_action_map)
        optimal_action = utility_action_map[max_utility]
    elif current_player == O:
        for action in possible_actions:
            value = max_value(result(board, action))
            utility_action_map[value] = action
            pass
        min_utility = min(utility_action_map)
        optimal_action = utility_action_map[min_utility]
    return optimal_action


def max_value(board):
    value = -1
    if terminal(board):
        return utility(board)
    for action in actions(board):
        value = max(value, min_value(result(board, action)))
    return value

def min_value(board):
    value = 1
    if terminal(board):
        return utility(board)
    for action in actions(board):
        value = min(value, max_value(result(board, action)))
    return value

