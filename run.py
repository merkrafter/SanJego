import os
import sys

MAX_WIDTH = 15
MAX_AREA = 15

rules = "base"

sizes = [(h, w) for w in range(1, MAX_WIDTH) for h in range(1, w + 1) if h * w <= MAX_AREA]

for height, width in sizes:
    return_value = os.system(f"python main.py with height={height} width={width}")
    if return_value != 0:
        sys.stderr.write("previous calculation failed\n")
        break

    # due to symmetry etc. only fields with an odd number of cells need to be
    # recalculated for the min player beginning
    if (height * width) % 2 == 0:
        return_value = os.system(f"python main.py with height={height} width={width} max_player_starts=False")
        if return_value != 0:
            sys.stderr.write("previous calculation failed\n")
            break
