from table import Size
from typing import Union, Any

class SizeError(Exception): pass

class Matrix:
    # == Basic utilities == #

    def __init__(self, *args, default_allow_nmul = False) -> None:
        '''Represents a matrix.'''
        
        # Type error protection
        if not all([isinstance(arg, Union[list, tuple]) for arg in args]) or \
           not all([all([isinstance(el, Union[int, float]) for el in line]) for line in args]):
            
            raise TypeError('Invalid type for a matrix entry. (Must be tuples/lists)')

        # Length error protection
        if not all(le == len(args[0]) for le in list(map(len, args))):
            raise SizeError(f'All matrix lines must have the same length.')
        
        if not len(args): raise SizeError('Matrix must have at least one line / column.')

        # Save
        self.content = list([list(line) for line in args])
        self.size = Size((len(self.content), len(self.content[0])))
        
        # Settings
        self.allow_nmul = default_allow_nmul

    def get_column(self, key: Union[int, Union[tuple, list]], content: list = None) -> list:
        '''Returns one or more columns from the matrix.'''
        
        if content is None: content = self.content
        
        size_x = len(content[0])
        
        # Simple int key: return the n column
        if isinstance(key, int):
            if key < 0: key = size_x + key
            return [l[key] for l in content]
        
        # Iterable key: acts like range() arguments
        keys = [v + size_x + 1 if v < 0 else v for v in list(key)]
        return [[l[i] for l in content] for i in range(*keys)]

    def reverse(self, content: list) -> list:
        '''Inverse the columns and lines.'''
        
        return self.get_column((0, -1), content)

    def join(self, content: list = None, deco: str = None, color_rule: dict = None, raw = True) -> None:
        '''Returns a raw, printable version of the matrix.'''
        
        boldify = True
        
        # Default decoration characters
        deco = deco or '│╭╮╰╯()'
        
        # Default color rules
        color_rule = color_rule or {
            lambda x: '\033[91m' if x < 0 else '',
            lambda x: '\033[0;32m' if x > 0 else '',
            lambda x: '\033[0;33m' if 'e' in str(x) else '',
            lambda x: '\033[0;34m' if isinstance(x, float) else '',
            lambda x: '\033[0m' if not x else ''
        } if color_rule is not False else {}
        
        def paint(el) -> str:
            for rule in color_rule:
                color = rule(el)
                if color: return f'{color}{el}\033[0m'
            
            return str(el)
        
        if content is None: content = self.content
        
        # get content per columns
        cols = self.get_column((0, -1), content)
        col_lens = [max([len(str(e)) for e in col]) for col in cols]
        
        # Stringify and colorize
        cols = [[f"{paint(el)}{' ' * (space - len(str(el)))}" for el in col]
                for col, space in zip(cols, col_lens)]
        
        # Rotate back to lines
        lines = self.reverse(cols)
        
        # Decorate
        lines = [f"{deco[0]}{' '.join(l)}{deco[0]}" for l in lines]     # body
        
        if len(lines) == 1:
            # If matrix has one line only
            lines[0] = deco[-2] + lines[0].replace(deco[0], '') + deco[-1]
        
        else:
            # For all other matrixes
            lines[0] = deco[1] + lines[0].replace(deco[0], '') + deco[2]    # Top
            lines[-1] = deco[3] + lines[-1].replace(deco[0], '') + deco[4]  # Bottom
        
        # Return
        return '\n'.join(lines) if raw else lines

    def print(self, content: list = None, deco: str = None, color_rule: dict = None, raw = True) -> None:
        '''Prints the matrix in a pretty form.'''
        
        print(self.join(content, deco, color_rule, raw))

    # == User utilities == #

    def __getitem__(self, key: int) -> list:
        '''Allow the user to modify the matrix as it was a 2D array.'''
        
        return self.content[int(key)]

    # == Operations == #

    def __add__(self, other) -> Any:
        '''Add two matrix together.'''
        
        other: Matrix
        
        # Error protection
        if not isinstance(other, Matrix): raise TypeError('Matrix addition must be between two matrixes.')
        
        # Size error protection
        if self.size.x != other.size.x or self.size.y != other.size.y:
            raise SizeError('During addition, matrixes must have the same size.')
        
        # Add
        for y, line in enumerate(other.content):
            for x, value in enumerate(line):
                self.__getitem__(y)[x] += value
        
        return self

    def __sub__(self, other) -> Any:
        '''handles substraction.'''
        
        return self.__add__(-1 * other)

    def __mul__(self, other, allow_nmul = False) -> Any:
        '''Handle matrix multiplication.'''
        
        other: Matrix
        
        # allow_nmul = False
        
        # Multiplication by a real
        if isinstance(other, Union[int, float]):
            if not allow_nmul: raise TypeError('Matrix multiplication must be real*Matrix, not Matrix*real.')
        
            for y, line in enumerate(self.content):
                for x, value in enumerate(line):
                    self.__getitem__(y)[x] *= other
            
            return self

        # Multiplication with another matrix
        elif isinstance(other, Matrix):
            
            # Error protection
            if self.size.y != other.size.x:
                raise SizeError('During matrix multiplication, m1.sizex must be equal to m2.size.y.')
            
            # Initialize empty matrix with right size
            result = [[0 for _ in range(other.size.y)] for _ in range(self.size.x)]
            
            for y, line in enumerate(result):
                for x, _ in enumerate(line):
                    
                    result[y][x] = sum(
                        [i * j for i, j in zip(self.content[y], self.reverse(other.content)[x])]
                    )
            
            return Matrix(*result)
        
        else: raise TypeError('Invalid type for multiplying with a Matrix.')

    def __rmul__(self, other) -> Any:
        '''Handle reverse multiplication with a real.'''
        
        if not isinstance(other, int): raise TypeError('Multiplication with a real must have the form real*Matrix.')
        
        return self.__mul__(other, allow_nmul = True)


# Default matrix presets

class Preset:
    class Null(Matrix):
        def __init__(self, size: Union[list, tuple]) -> None:
            
            cnt = [[0 for _ in range(size[1])] for _ in range(size[0])]
            
            super().__init__(*cnt)
    
    class Neutral(Matrix):
        def __init__(self, size: int) -> None:
            
            if not isinstance(size, int): raise TypeError('Neutral matrixes must be squared.')
            
            # Fill with zeroes
            cnt = [[0 for _ in range(size)] for _ in range(size)]
            
            # Add ones
            for i in range(size): cnt[i][i] = 1
            
            super().__init__(*cnt)


if __name__ == '__main__':
    print(f'Please import {__file__} as a module.')
