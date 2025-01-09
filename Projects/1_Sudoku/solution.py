from utils import *
import copy

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Initialize the diagonal units
diagonal1 = []
diagonal2 = []

# Generate the first diagonal (top-left to bottom-right)
for i in range(len(rows)):
    diagonal1.append(rows[i] + cols[i])

# Generate the second diagonal (top-right to bottom-left)
for i in range(len(rows)):
    diagonal2.append(rows[i] + cols[-i-1])

# Combine the diagonal units
diagonal_units = [diagonal1, diagonal2]

unitlist = row_units + column_units + square_units + diagonal_units

# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strat repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    # Create a deep copy of values
    out = copy.deepcopy(values)
    for boxA in values:
        for boxB in peers[boxA]:
            if(values[boxA] == values[boxB] and len(values[boxA]) == 2):
                common_peers = set(peers[boxA]).intersection(peers[boxB])
                for peer in common_peers:
                     for digit in values[boxA]:
                            if digit in out[peer]:
                                out[peer] = out[peer].replace(digit, '')
    return out                         

def get_keys_with_single_value(d):
    return [key for key, value in d.items() if len(value) == 1]
    
def remove_single_value_from_peers(d, key):
    single_value = d[key]
    for peer in peers[key]:
        if single_value in d[peer]:
            d[peer] = d[peer].replace(single_value, '')
    return d

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    single_value_keys = get_keys_with_single_value(values)
    for key in single_value_keys:
        d = remove_single_value_from_peers(values, key)
    return d


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # Dictionary to store possible positions for each digit in each unit
    digit_positions = {digit: [] for digit in '123456789'}
    
    for unit in unitlist:
        # Reset digit positions for the current unit
        for digit in '123456789':
            digit_positions[digit] = []
        
        # Find all possible positions for each digit in the current unit
        for box in unit:
            for digit in '123456789':
                if digit in values[box]:
                    digit_positions[digit].append(box)
        
        # Assign the digit if there's only one possible position
        for digit, positions in digit_positions.items():
            if len(positions) == 1:
                values[positions[0]] = digit

    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    def is_solved(values):
        """Check if the puzzle is solved."""
        return all(len(values[box]) == 1 for box in values)
    
    def has_empty_boxes(values):
        """Check if there are any boxes with zero available values."""
        return any(len(values[box]) == 0 for box in values)
    
    stalled = False
    while not stalled:
        solved_values_before = sum(len(values[box]) == 1 for box in values)
        
        # Apply the Eliminate Strategy
        values = eliminate(values)
        
        # Apply the Only Choice Strategy
        values = only_choice(values)
        
        # Check how many boxes have a determined value, to compare
        solved_values_after = sum(len(values[box]) == 1 for box in values)
        
        # Check if no new values were added
        stalled = solved_values_before == solved_values_after
        
        # Check for any boxes with zero available values
        if has_empty_boxes(values):
            return False
        
        # Check if the puzzle is solved
        if is_solved(values):
            return values

    return values

def solve_sudoku(values, min_box):
    """Helper function to solve the Sudoku puzzle using recursion."""
    for value in values[min_box]:
        new_sudoku = values.copy()
        new_sudoku[min_box] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt
    return False

def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # First, reduce the puzzle using the previous function including the naked twins
    values = reduce_puzzle(naked_twins(values))
    
    # If the puzzle is unsolvable, return False
    if values is False:
        return False
    
    # If the puzzle is solved, return the solution
    if all(len(values[s]) == 1 for s in boxes): 
        return values  # Solved!
    
    # Choose one of the unfilled squares with the fewest possibilities
    min_len = float('inf')
    min_box = None
    for box in boxes:
        if len(values[box]) > 1 and len(values[box]) < min_len:
            min_len = len(values[box])
            min_box = box
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    return solve_sudoku(values, min_box)

def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)
    
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
