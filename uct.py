from Connect4 import ConnectFour

def uct(obs):
    """
    Agent function : uses connect4 game code to estimate values of next moves
    Inputs : 
      - obs : kaggle object describing the game state 
    Outputs : 
      - number between 0 and 6 describing the connect 4 action
    """
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

        # Rollout
        while state.get_result(pjm) is None:  # while state is non-terminal
            state.do_move(state.get_random_move())
        
        # Backpropagate
        # backpropagate from the expanded node and work back to the root node
        while node is not None:
            node.update(state.get_result(node.player_just_moved))
            node = node.parentNode

        # Testing Time : stop if remaining time to 2s is below time required to do two times the last iterations
        if (2 - (time.time() - start)) < 2 * (time.time() - looptime):
            notend = False
    # Output some information about the tree - can be omitted
    if verbose == 2:
        print(rootnode.tree_to_string(0))
    elif verbose == 1:
        print(rootnode.children_to_string())
    # return the move that was most visited
    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move
