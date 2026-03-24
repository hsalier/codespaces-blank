# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from .core import CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction, PlayerColor
from .utils import render_board


def search(
    board: dict[Coord, CellState]
) -> list[Action] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to `CellState` instances (each with a `.color` and
            `.height` attribute).

    Returns:
        A list of actions (MoveAction, EatAction, or CascadeAction), or `None`
        if no solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))
    board = apply(board, MoveAction(Coord(3, 3), Direction.Down))
    print("next board")
    print(render_board(board, ansi=True))
    board = apply(board, EatAction(Coord(4, 3), Direction.Down))
    print("next board")
    print(render_board(board, ansi=True))
    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    # ...

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return [
        MoveAction(Coord(3, 3), Direction.Down),
        EatAction(Coord(4, 3), Direction.Down),
    ]

def apply(board: dict[Coord, CellState], action: Action) -> dict[Coord, CellState]:
    """
    this function will make a valid move on the board
    parameters: 
        `board`: explained above
        `action`: either a MoveAction, EatAction, or CascadeAction to be performed
                  this action must ALREADY be known to be a valid move ! this function 
                  will not check if the move to be performed is valid.  
    returns:
        the new updated board state :-)
    """
    new_board = dict(board)

    match action:    
        case MoveAction(coord, direction):
            source = new_board.pop(coord)
            dest = coord + direction
            
            # if there's a red piece in the square -> merge
            if dest in new_board:
                    curr = new_board[dest]
                    new_board[dest] = CellState(PlayerColor.RED, source.height + curr.height)
            
            # otherwise, square is empty (no blue already guaranteed by valid_move checker)
            else:
                    new_board[dest] = source
            
        case EatAction(coord, direction):
              source = new_board.pop(coord)
              dest = coord + direction
              new_board[dest] = CellState(PlayerColor.RED, source.height)
            
    return new_board
              

