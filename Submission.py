def uct(obs, config, verbose=0):
    import numpy as np
    import random
    import math
    import time

    def _indent_string(indent):
        s = "\n"
        for i in range(1, indent+1):
            s += "| "
        return s
    
    class ConnectFour:
        """
        Class for creating a connect four game
        """

        def __init__(self, height=6, width=7, board=[[0 for x in range(7)] for i in range(6)], player_just_moved=2):
            self.height = height
            self.width = width
            self.board = board
            self.player_just_moved = player_just_moved

        def clone(self):
            """ Create a deep clone of this game state.
            """
            st = ConnectFour()
            st.board = [self.board[i] for i in range(self.height)]
            st.player_just_moved = self.player_just_moved
            return st

        def get_column(self, index):
            """
            Returns a column at the specified index

            :param index: Index at which column will be returned
            """
            return [i[index] for i in self.board]

        def get_row(self, index):
            """
            Returns a row at the specified index

            :param index: Index at which row will be returned
            """
            return self.board[index]

        def get_diagonals(self):
            """
            Returns all the diagonals in the game
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

        def get_moves(self):
            legal_moves = []
            if self.get_result(1) not in [0.,1.]:
                for i in range(self.width):
                    if self.board[0][i] == 0:
                        legal_moves.append(i)
            return legal_moves

        def do_move(self, col):
            """
            Simulates a move and puts a 1/2 in the specified column
            """
            #         if ' ' not in self.get_column(col):
            #             return self.board
            i = self.height - 1
            while self.board[i][col] != 0:
                i -= 1
            self.player_just_moved = 3 - self.player_just_moved
            self.board[i][col] = self.player_just_moved
            return self.board

        def get_random_move(self):
            return np.random.choice(self.get_moves())
        
        def get_result(self, playerjm):
            """
            Checks self.board if either user has four in a row
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

            if 0 not in self.board[0]:
                win = 0.5
                    
            return win

    class Node:
        """
        A node in the game tree. Note wins is always from the viewpoint of
        player_just_moved. Crashes if state not specified.
        """

        def __init__(self, move=None, parent=None, state=None):
            # the move that got us to this node - "None" for the root node
            self.move = move
            self.parentNode = parent  # "None" for the root node
            self.childNodes = []
            self.wins = 0
            self.visits = 0
            self.untried_moves = state.get_moves()
            # future child nodes
            # the only part of the state that the Node needs later
            self.player_just_moved = state.player_just_moved

        def uct_select_child(self):
            """
            Use the UCB formula to select a child node. Often a constant UCTK is
            applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits
            to vary the amount of exploration versus exploitation.
            """
            s = sorted(self.childNodes,
                       key=lambda c:
                       c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))[-1]
            return s

        def add_child(self, m, s):
            """ Remove m from untried_moves and add a new child node for this move.
                Return the added child node
            """
            n = Node(move=m, parent=self, state=s)
            self.untried_moves.remove(m)
            self.childNodes.append(n)
            return n

        def update(self, result):
            """
            update this node - one additional visit and result additional wins.
            result must be from the viewpoint of player_just_moved.
            """
            self.visits += 1
            self.wins += result

        def __repr__(self):
            return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" \
                   + str(self.visits) + " U:" + str(self.untried_moves) + "]"

        def tree_to_string(self, indent):
            s = _indent_string(indent) + str(self)
            for c in self.childNodes:
                s += c.tree_to_string(indent + 1)
            return s

        def children_to_string(self):
            s = ""
            for c in self.childNodes:
                s += str(c) + "\n"
            return s

    def whotoplay(obs):
        board = obs.board
        if board.count(2) == board.count(1):
            return 1
        else:
            return 2

    def board_from_obs(obs):
        root_board = []

        for i in range(6):
            root_board.append([obs.board[j] for j in range(7 * i, 7 * i + 7)])
        return root_board


    start=time.time()
    notend = True
    pjm = 3 - whotoplay(obs)

    root_board = board_from_obs(obs)
    print(root_board)
    root_state = ConnectFour(board=root_board, player_just_moved=pjm)
    copy_rootnode = Node(state=root_state)
    child_number = len(copy_rootnode.untried_moves)

    rootnode = Node(state=root_state)
    while notend:
        looptime = time.time()
        node = rootnode
        root_board = board_from_obs(obs)
        state = ConnectFour(board=root_board, player_just_moved=pjm)  
        # Select
        # node is fully expanded and non-terminal
        while node.untried_moves == [] and node.childNodes != []:
            node = node.uct_select_child()
            state.do_move(node.move)

        # Expand
        # if we can expand (i.e. state/node is non-terminal)
        if len(node.untried_moves) > 0:
            m = random.choice(node.untried_moves)
            state.do_move(m)
            node = node.add_child(m, state)  # add child and descend tree
            node.visits = 100 // (4 * child_number)
            node.wins = node.visits // 2

        # Rollout - this can often be made orders of magnitude quicker using a
        # state.GetRandomMove() function
        while state.get_result(pjm) is None:  # while state is non-terminal
            state.do_move(state.get_random_move())
        
        # Backpropagate
        # backpropagate from the expanded node and work back to the root node
        while node is not None:
            # state is terminal. update node with result from POV of
            # node.player_just_moved
            node.update(state.get_result(node.player_just_moved))
            node = node.parentNode

        # Testing Time : stop if remaining time to 2s is below time required to do two iterations with same time as this loop
        if (2 - (time.time() - start)) < 2 * (time.time() - looptime):
            notend = False
    # Output some information about the tree - can be omitted
    if verbose == 2:
        print(rootnode.tree_to_string(0))
    elif verbose == 1:
        print(rootnode.children_to_string())
    # return the move that was most visited
    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move

