# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from .core import CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction, PlayerColor, BOARD_N
from .utils import render_board
import heapq
from dataclasses import dataclass

#Amy: class to represent nodes in tree
@dataclass
class Node:
    state: dict[Coord, CellState]
    parent: 'Node | None' = None      # default None
    action: Action | None = None       # default None
    g: int = 0                         # default 0
    h: int = 0                         # default 0

    @property
    def f(self) -> int:
        return self.g + self.h

    def __lt__(self, other):
        return self.f < other.f
    

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
    board_copy = board
    counter = 0
    start = Node(state=board, g=0, h=heuristic(board))

    # (f, inadmissable h, counter, node) — inadmissable is a tiebreaker for equal f values, defaults to counter
    pq = [(start.f, -start.g, counter, start)]
    visited = set()
    while pq:
        _, _, _, node = heapq.heappop(pq)

        state_key = frozenset(node.state.items())
        if state_key in visited:
            continue
        visited.add(state_key)

        if is_goal(node.state):
            x = reconstruct_path(node)
            for action in x:
                board_copy = apply(board_copy, action)
                print(render_board(board_copy, ansi=True))
            return x

        for action in get_legal_actions(node.state):
            new_state = apply(node.state, action)
            new_key = frozenset(new_state.items())
            if new_key not in visited:
                child = Node(
                    state=new_state,
                    parent=node,
                    action=action,
                    g=node.g + 1,
                    h=heuristic(new_state)
                )
                counter += 1
                heapq.heappush(pq, (child.f, -child.g, counter, child))

    return None

def heuristic(board):
    # Build adjacency: row -> [columns with blues in that row]
    adj = {}
    has_blue = False
    for coord, cell in board.items():
        if cell.color == PlayerColor.BLUE:
            has_blue = True
            if coord.r not in adj:
                adj[coord.r] = []
            adj[coord.r].append(coord.c)

    if not has_blue:
        return 0

    # Maximum bipartite matching via augmenting paths
    # By König's theorem, this equals the minimum vertex cover,
    # which equals the minimum number of row/column lines to cover all blues
    match_col = {}  # col -> matched row

    def try_augment(row, visited):
        for col in adj.get(row, []):
            if col in visited:
                continue
            visited.add(col)
            if col not in match_col or try_augment(match_col[col], visited):
                match_col[col] = row
                return True
        return False

    matching = 0
    for row in adj:
        if try_augment(row, set()):
            matching += 1

    return matching

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

            # iterate through range of tiles that will 
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
    eats = []
    cascades = []
    moves = []

    blues = {c for c, cell in state.items() if cell.color == PlayerColor.BLUE}
    if not blues:
        return []

    for coord, cell in state.items():
        if cell.color != PlayerColor.RED:
            continue

        for direction in Direction:
            try:
                dest = coord + direction
                dest_cell = state.get(dest, CellState())

                # only consider actions that move "towards" at least one blue
                gets_closer = any(
                    abs(dest.r - b.r) + abs(dest.c - b.c) <
                    abs(coord.r - b.r) + abs(coord.c - b.c)
                    for b in blues
                )

                if not gets_closer:
                    continue

                # EAT: allowed when adjacent square is blue and red is tall enough
                if (
                    dest_cell.color == PlayerColor.BLUE
                    and cell.height >= dest_cell.height
                ):
                    eats.append(EatAction(coord, direction))

                # MOVE: allowed into empty or red square
                if dest_cell.is_empty or dest_cell.color == PlayerColor.RED:
                    moves.append(MoveAction(coord, direction))

                # CASCADE: allowed whenever red stack has height >= 2
                # and the direction gets closer to at least one blue
                if cell.height >= 2:
                    cascades.append(CascadeAction(coord, direction))

            except ValueError:
                pass

    return eats + cascades + moves


def reconstruct_path(node: Node) -> list:
    """Walk back up the parent chain to build the action sequence."""
    actions = []
    while node.parent is not None:
        actions.append(node.action)
        node = node.parent
    actions.reverse()
    return actions

