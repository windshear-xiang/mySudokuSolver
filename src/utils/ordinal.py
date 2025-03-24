import numpy as np
from numba import njit
        
class Ordinal:
    # Dictionary to convert digits to their superscript representation
    super_dict = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}

    def __init__(self, array):
        if len(array) == 0:
            array = [0]
        self.array = np.array(array, dtype=np.int64)  # Store the input array as a numpy array
        self.order = len(self.array)  # Length of the array determines the order

    @classmethod
    def to_superscript(cls, i):
        # Convert a number to its superscript string representation
        return ''.join(cls.super_dict[digit] for digit in str(i))

    def __str__(self):
        # Construct the ordinal notation as a string
        if self == Ordinal([0]):
            return '0'
        return '+'.join([
            f'{n}' if i == 0 else f'ω{Ordinal.to_superscript(i) if i > 1 else ""}{n if n > 1 else ""}' 
            for i, n in enumerate(self.array) if n != 0
        ][::-1])
    
    @staticmethod
    @njit
    def _eq_numba(a1: np.ndarray, a2: np.ndarray):
        if len(a1) != len(a2):
            return False
        for i in range(len(a1)):
            if a1[i] != a2[i]:
                return False
        return True
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Ordinal):
            return Ordinal._eq_numba(self.array, other.array)
        return NotImplemented
    
    @staticmethod
    @njit
    def _add_numba(a1: np.ndarray, a2: np.ndarray):
        len_a2 = len(a2)
        part1 = a2[:-1]
        part2 = np.array([a2[-1] + a1[len_a2 - 1]], dtype=np.int64)
        part3 = a1[len_a2:]
        return np.concatenate((part1, part2, part3))

    def __add__(self, other):
        if isinstance(other, Ordinal):
            if self.order < other.order:
                return other
            new_array = Ordinal._add_numba(self.array, other.array)
            return Ordinal(new_array)
        elif isinstance(other, int):
            return self + Ordinal([other])
        return NotImplemented
    
    def __radd__(self, other):
        if isinstance(other, int):
            return Ordinal([other]) + self
        return NotImplemented
    
    @staticmethod
    @njit
    def _mul_numba(a1: np.ndarray, a2: np.ndarray):
        part1 = a1[:-1]
        part2 = np.array([a1[-1] * a2[0]], dtype=np.int64)
        part3 = a2[1:]
        return np.concatenate((part1, part2, part3))
    
    def __mul__(self, other):
        if self == Ordinal([0]) or other == Ordinal([0]):
            return Ordinal([0])
        if isinstance(other, Ordinal):
            new_array = Ordinal._mul_numba(self.array, other.array)
            return Ordinal(new_array)
        elif isinstance(other, int):
            return self * Ordinal([other])
        return NotImplemented
    
    def __rmul__(self, other):
        if isinstance(other, int):
            return Ordinal([other]) * self
        return NotImplemented
    
    @staticmethod
    @njit
    def _digit2ord_numba(digit):
        temp = []
        for i in range(3):
            if 3 ** i > digit:
                break
            val = (digit // (3 ** i)) % 3
            temp.append(val)
        return np.array(temp, dtype=np.int64)

    @staticmethod
    def digit2ord(digit):
        # Convert a single digit to an Ordinal object
        return Ordinal(Ordinal._digit2ord_numba(digit))
    
    @staticmethod
    def prod(l):
        ret = Ordinal.digit2ord(1)
        for i in l:
            ret *= i
        return ret

def print_board_in_ord(board):
    print("    0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  ")
    for i, row in zip(range(9), board):
        print(f"{i} |{'|'.join([str(Ordinal.digit2ord(digit)).ljust(4) for digit in row])}|")
        print("--+----+----+----+----+----+----+----+----+----+")
    return