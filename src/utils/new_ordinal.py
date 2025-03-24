import numpy as np
from numba import njit, int32
from numba.experimental import jitclass

super_dict = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}

def to_superscript(num: int):
    '''Convert a number to its superscript string representation'''
    return ''.join(super_dict[digit] for digit in str(num))

spec = [
    ("array", int32[:]),
    ("order", int32)
]

@jitclass(spec) # type: ignore
class Ordinal:
    def __init__(self, array):
        self.order = len(array)
        if self.order == 0:
            self.array = np.array([0], dtype=np.int32)
        else:
            self.array = np.array(array, dtype=np.int32)
    
    def __str__(self):
        '''Construct the ordinal notation as a string'''
        if self == Ordinal([0]):
            return '0'
        return '+'.join([
            f'{n}' if i == 0 else f'ω{to_superscript(i) if i > 1 else ""}{n if n > 1 else ""}' 
            for i, n in enumerate(self.array) if n != 0
        ][::-1])
    
    def __eq__(self, other):
        if not isinstance(other, Ordinal):
            return NotImplemented
        if self.order != other.order:
            return False
        for i in range(self.order):
            if self.array[i] != other.array[i]:
                return False
        return True