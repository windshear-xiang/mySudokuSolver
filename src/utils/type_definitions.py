'''
This module provide useful type annotations `NumBoard`, `CandBoard`, `TufBoard`, and `Position`
'''

import numpy as np
from typing import Annotated, Tuple
from numpy.typing import NDArray

NumBoard = Annotated[NDArray[np.int8], (9, 9)]
CandBoard = Annotated[NDArray[np.bool_], (9, 9, 9)]
TufBoard = Annotated[NDArray[np.int8], (9, 9, 9)]
Position = Tuple[int|np.intp, int|np.intp]