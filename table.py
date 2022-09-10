from copy import copy
from typing import Union, Any

# === Utilities === #

class AxisTuple:
    def __init__(self, tup: tuple, name: str = 'AxisTuple') -> None:
        self._type = name
        self.x, self.y = tup
        self.__setattr__(name, tup)
    def __str__(self) -> str: return str(self.__getattribute__(self._type))

class Size(AxisTuple):
    def __init__(self, size) -> None: super().__init__(size, 'size')

class Pos(AxisTuple):
    def __init__(self, *pos) -> None: super().__init__(pos, 'pos')

def parse_rel(index, _max) -> int:
    
    # Positive numbers
    if index > 0:
        if index < 0.98: index = int(round(index * _max, 0))
        else: index = -1 # somehow is needed
            
    # Negative numbers
    else: index = int(round(index * _max, 0))
    
    return index

# === Table class === #

class Table:
    class Pixel:
        def __init__(self, value: Any, pos: Union[Pos, tuple]) -> None:
            # Representation of a pixel
            self.value = copy(value) # Copy in case of class use
            self.pos = pos if isinstance(pos, Pos) else Pos(pos)
        
        def __str__(self) -> str: return str(self.value)
        def __repr__(self) -> str: return str(self.value)
    
    class Column:
        def __init__(self, keys, key) -> None:
            # Representation of a column.
            
            self.keys = keys
            self.pos = key
            self.size = len(self.keys)
        
        def __getitem__(self, key: Union[int, float]) -> Any:
            if isinstance(key, float): key = parse_rel(key, self.size)
            # super().__getitem__(self, key)
            return self.keys[key]
        
        #def __setitem__(self, key: Union[int, float], value: str) -> Any:
            #if isinstance(key, float): key = parse_rel(key, self.size)
            # super().__setitem__(self, key, value)
        
        def __setitem__(self, key, value) -> Any:
            if isinstance(key, float): key = parse_rel(key, self.size)
            self.keys[key].value = value
            
    def __init__(self, size: Union[tuple, str], default: Any = '') -> None:
        '''
        Represents a table that can only be filled with a one-long character
        value in each field.
        '''
        
        # Init size
        if isinstance(size, str): size = list(map(int, size.split('x')))
        self.size = Size(size)
        
        # Init table
        self.table = [[Table.Pixel(default, Pos(x, y)) for x in range(self.size.x)]
                      for y in range(self.size.y)]
    
    def __getitem__(self, index: Union[int, float]) -> Any:
        # Returns a column
        
        # Error protection
        if not type(index) in (int, float): raise TypeError('Invalid index type.')
        
        # Relative value
        if isinstance(index, float): index = parse_rel(index, self.size.x)
        
        # List method
        # return [l[index] for l in self.table]
        
        # Column method
        return Table.Column([l[index] for l in self.table], index)
    
    def join(self, seps = ('\n', '')) -> str:
        # Returns the current raw version of table.
        
        res = ''
        for l in self.table: res += seps[1].join(map(str, l)) + seps[0]
        
        return res[:-1]
    
    # Outputs the current raw version of the table.
    def print(self) -> None: print(self.join())
    def __str__(self) -> str: return self.join()
    def __repr__(self) -> str: return self.join()
