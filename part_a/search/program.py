# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from .core import CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction, PlayerColor, BOARD_N
from .utils import render_board

#Amy
@dataclass
class Node:
    state: dict[Coord, CellState]
    parent: 'Node | None'
    action: Action | None
    g: int   # cost so far
    h: int   # heuristic

#Amy added
def is_goal(state: dict[Coord, CellState]) -> bool:
    """
    Return True if there are no Blue stacks left on the board.
    Return False otherwise.
    """
    for cell in state.values():
        if cell.color == PlayerColor.BLUE:
            return False
    return True

#Amy added
def get_legal_actions(state: dict[Coord, CellState]) -> list[Action]:
    """
    Return all legal actions available to Red from the given board state.

    Legal actions:
    - MOVE into an adjacent empty cell
    - MOVE into an adjacent Red stack (merge)
    - EAT an adjacent Blue stack if red.height >= blue.height
    - CASCADE in any direction if the Red stack height is at least 2
    """
    legal_actions: list[Action] = []

    for coord in sorted(state.keys()):
        cell = state[coord]

        # Only Red stacks can act
        if cell.color != PlayerColor.RED:
            continue

        for direction in Direction:
            # --- MOVE / EAT depend on the adjacent destination being on-board ---
            try:
                dest = coord + direction
                dest_cell = state.get(dest, CellState())

                # MOVE: destination empty or friendly Red stack
                if dest_cell.is_empty or dest_cell.color == PlayerColor.RED:
                    legal_actions.append(MoveAction(coord, direction))

                # EAT: destination Blue stack and attacker tall enough
                elif (
                    dest_cell.color == PlayerColor.BLUE
                    and cell.height >= dest_cell.height
                ):
                    legal_actions.append(EatAction(coord, direction))

            except ValueError:
                # Off-board for MOVE/EAT, so do nothing here
                pass

            # --- CASCADE ---
            # Allowed for any Red stack of height >= 2 in any direction
            if cell.height >= 2:
                legal_actions.append(CascadeAction(coord, direction))

    return legal_actions


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
    board = apply(board, MoveAction(Coord(5, 6), Direction.Up))
    board = apply(board, MoveAction(Coord(4, 6), Direction.Up))
    board = apply(board, MoveAction(Coord(3, 6), Direction.Up))
    board = apply(board, MoveAction(Coord(2, 6), Direction.Up))
    board = apply(board, MoveAction(Coord(1, 6), Direction.Up))
    board = apply(board, MoveAction(Coord(0, 6), Direction.Left))
    board = apply(board, MoveAction(Coord(0, 5), Direction.Left))
    board = apply(board, MoveAction(Coord(0, 4), Direction.Left))
    board = apply(board, MoveAction(Coord(0, 3), Direction.Left))
    board = apply(board, MoveAction(Coord(0, 2), Direction.Left))
    board = apply(board, MoveAction(Coord(0, 1), Direction.Left))
    print(render_board(board, ansi=True))
    board = apply(board, CascadeAction(Coord(0, 0), Direction.Down))
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

        case CascadeAction(coord, direction):
            source = new_board.pop(coord)
            h = source.height

            for i in range(1, h + 1):
                r = coord.r + direction.r * i
                c = coord.c + direction.c * i
                if not (0 <= r < BOARD_N and 0 <= c < BOARD_N):
                    break
                pos = Coord(r, c)
                if pos in new_board:
                    push(new_board, pos, direction)
                new_board[pos] = CellState(PlayerColor.RED, 1)

              
            
    return new_board
              

def push(board, coord, direction):
    nr = coord.r + direction.r
    nc = coord.c + direction.c
    if not (0 <= nr < BOARD_N and 0 <= nc < BOARD_N):
        board.pop(coord)
        return
    dest = Coord(nr, nc)
    if dest in board:
        push(board, dest, direction)
    board[dest] = board.pop(coord)
