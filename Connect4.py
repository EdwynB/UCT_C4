import copy
import numpy as np

class ConnectFour:
    """
    Connect four game's class
    """

    def __init__(self, height=6, width=7, player_just_moved=2):
        self.height = height
        self.width = width
        self.board = [[0 for x in range(width)] for i in range(height)]
        self.player_just_moved = player_just_moved

    def clone(self):
        """
        Create a deep clone of this game state.
        """
        st = ConnectFour()
        st.board = copy.deepcopy(self.board)
        st.player_just_moved = self.player_just_moved
        return st

    def get_column(self, index):
        """
        Returns the board column at the specified index

        :param index: Index at which column will be returned
        """
        return [i[index] for i in self.board]

    def get_row(self, index):
        """
        Returns the board row at the specified index

        :param index: Index at which row will be returned
        """
        return self.board[index]

    def get_diagonals(self):
        """
        Returns all the diagonals of the board
        """

        diagonals = []

        for i in range(self.height + self.width - 1):
            diagonals.append([])
            for j in range(max(i - self.height + 1, 0), min(i + 1, self.height)):
                diagonals[i].append(self.board[self.height - i + j - 1][j])

        for i in range(self.height + self.width - 1):
            diagonals.append([])
            for j in range(max(i - self.height + 1, 0), min(i + 1, self.height)):
                diagonals[i].append(self.board[i - j][j])

        return diagonals

    def get_winning_moves(self):
        """
        Returns all winning move of the current board
        """
        winning_moves = []
        for m in self.get_moves():
            c4 = self.clone()
            c4.do_move(m)
            if c4.get_result(1) is not None:
                winning_moves.append(m)
        return winning_moves

    def get_moves(self):
        """
        Returns all legal moves of the current board
        """
        legal_moves = []
        for i in range(self.width):
            if self.board[0][i] == 0:
                legal_moves.append(i)
        return legal_moves

    def do_move(self, col):
        """
        Simulates a move and puts a 1/2 in the specified column
        """
        i = self.height - 1
        while self.board[i][col] != 0:
            i -= 1
        self.player_just_moved = 3 - self.player_just_moved
        self.board[i][col] = self.player_just_moved
        return self.board

    def get_random_win_move(self):
        """
        Returns a winning move if such exists, random if not
        """
        wm = self.get_winning_moves()
        if len(wm) > 0:
            return wm[0]
        return np.random.choice(self.get_moves())

    def get_random_move(self):
        """
        Returns a random move
        """
        return np.random.choice(self.get_moves())

    def get_result(self, playerjm):
        """
        Checks self.board if either user has four in a row or if there is a tie
        """

        four_in_a_row = [[2, 2, 2, 2], [1, 1, 1, 1]]
        np_board = np.array(self.board)
        win = None

        # Check rows
        for i in range(self.height):
            for j in range(self.width - 3):
                if self.get_row(i)[j:j + 4] in four_in_a_row:
                    if self.board[i][j] == playerjm:
                        return 1.0
                    else:
                        return 0.0

        # Check columns
        for i in range(self.width):
            for j in range(self.height - 3):
                if self.get_column(i)[j:j + 4] in four_in_a_row:
                    if self.board[j][i] == playerjm:
                        return 1.0
                    else:
                        return 0.0

        # positive diagonal
        for row in range(self.height - 3):
            for col in range(self.width - 3):
                window = list(np_board[range(row, row + 4), range(col, col + 4)])
                if window.count(playerjm) == 4:
                    return 1.0
                elif window.count(3 - playerjm) == 4:
                    return 0.0

        # negative diagonal
        for row in range(3, self.height):
            for col in range(self.width - 3):
                window = list(np_board[range(row, row - 4, -1), range(col, col + 4)])
                if window.count(playerjm) == 4:
                    return 1.0
                elif window.count(3 - playerjm) == 4:
                    return 0.0

        if 0 not in np_board.flat:
            win = 0.5

        return win
