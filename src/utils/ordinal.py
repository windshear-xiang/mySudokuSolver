import numpy as np
from numba import njit, int32
from numba.experimental import jitclass

@njit
def to_superscript(num):
    """在 nopython 模式下，将数字转换为上标字符串表示"""
    super_dict = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹'
    }
    s = str(num)
    result = ""
    for ch in s:
        result += super_dict[ch]
    return result

spec = [
    ('array', int32[:]),
    ('order', int32),
]

@jitclass(spec=spec) # type: ignore
class Ordinal:
    def __init__(self, array):
        self.order = len(array)
        if self.order == 0:
            self.array = np.asarray([0], dtype=np.int32)
        else:
            self.array = np.asarray(array, dtype=np.int32)
        
    def __eq__(self, other):
        if not isinstance(other, Ordinal):
            raise NotImplementedError
        if self.order != other.order:
            return False
        for i in range(self.order):
            if self.array[i] != other.array[i]:
                return False
        return True

    def __str__(self):
        '''Construct the ordinal notation as a string'''
        if self == Ordinal([0]):
            return '0'
        return '+'.join([
            f'{n}' if i == 0 else f'ω{to_superscript(i) if i > 1 else ""}{str(n) if n > 1 else ""}' 
            for i, n in enumerate(self.array) if n != 0
        ][::-1])
    
    def __add__(self, other):
        if isinstance(other, Ordinal):
            if self.order < other.order:
                return other
            new_array = np.concatenate((
                other.array[:-1],
                np.asarray([other.array[-1] + self.array[other.order - 1]], dtype=np.int32),
                self.array[other.order:]
            ))
            return Ordinal(new_array)
        elif isinstance(other, int):
            return self + Ordinal([other])
        else:
            raise NotImplementedError
    
    def __radd__(self, other):
        if isinstance(other, int):
            return Ordinal([other]) + self
        raise NotImplementedError
    
    def __mul__(self, other):
        if isinstance(other, int):
            return self * Ordinal([other])
        elif self == Ordinal([0]) or other == Ordinal([0]):
            return Ordinal([0])
        elif isinstance(other, Ordinal):
            new_array = np.concatenate((
                self.array[:-1],
                np.asarray([self.array[-1] * other.array[0]], dtype=np.int32),
                other.array[1:]
            ))
            return Ordinal(new_array)
        else:
            raise NotImplementedError
    
    def __rmul__(self, other):
        if isinstance(other, int):
            return Ordinal([other]) * self
        raise NotImplementedError

@njit
def digit2ord(digit):
    '''Convert a single digit in an Ord-3 sudoku board to an Ordinal object'''
    return Ordinal([digit // 3 ** i % 3 for i in range(3) if digit >= 3 ** i])

def print_board_in_ord(board):
    print("    0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  ")
    for i, row in zip(range(9), board):
        print(f"{i} |{'|'.join([str(digit2ord(digit)).ljust(4) for digit in row])}|")
        print("--+----+----+----+----+----+----+----+----+----+")
    return

# 导入模块时强行预编译
_ = digit2ord(6) + Ordinal(np.array([0,2])) * Ordinal(np.array([0,1,2]))
