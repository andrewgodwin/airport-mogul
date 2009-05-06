
class LocDict(object):
    
    """
    A 'location dictionary', i.e. one that contains items referenced by location
    (their sets of covered squares). Should probably be a quadtree.
    """
    
    def __init__(self):
        
        self._grid = []
        self._items = {}
        self.size = [0, 0]
    
    
    def grow_to_size(self, width, height):
        "Increases the size of the items grid to the given size."
        
        # Extend it in the x direction
        if width > self.size[0]:
            self._grid.extend([[None] * max(height, self.size[1]) for i in range(width - len(self._grid))])
            self.size[0] = width
        # And the y direction
        if height > self.size[1]:
            for column in self._grid:
                column.extend([None] * (height - len(column)))
            self.size[1] = height
    
    
    def add(self, x, y, item):
        "Adds an item to the LocDict at the given coords."
        # Make sure we're big enough.
        self.grow_to_size(x+1, y+1)
        # Remove anything previously there
        self.clear(x, y)
        # Add it to the grid and list of items.
        self._grid[x][y] = item
        if item not in self._items:
            self._items[item] = [(x, y)]
        else:
            self._items[item].append((x, y))
    
    
    def clear(self, x, y):
        "Removes whatever was at x, y."
        item = self._grid[x][y]
        if item is not None:
            self._grid[x][y] = None
            self._items[item].remove((x, y))
            if not self._items[item]:
                del self._items[item]
    
    
    def get(self, x, y):
        "Returns the item at (x, y)"
        try:
            return self._grid[x][y]
        except IndexError:
            return None
    
    
    def __iter__(self):
        return iter(self._items)
    
    
    def items(self):
        return self._items.items()
    
    
    def coords_for_item(self, item):
        return self._items[item]



class ItemDict(LocDict):
    
    """
    A subclass of LocDict that tracks items - things with predefined floor
    patterns. Each Item has a .shape attribute which gives which squares
    it occupies relative to the origin and rotation.
    """
    
    def __init__(self):
        
        LocDict.__init__(self)
    
    
    def add(self, x, y, rot, item):
        """
        Adds the item at x,y with rotation rot (one of 0, 1, 2, 3 - number
        of 90deg rotations anticlockwise.)
        """
        pass


    
class DoorDict(object):
    
    "Stores a set of 'doors' (i.e. wall segments - (1,2) to (2,2))"
    
    def __init__(self):
        self.doors = set()
    
    
    def normalise(self, x, y, x2, y2):
        "Ensures coordinates are always in a consistent order."
        if x > x2:
            x, y, x2, y2 = x2, y2, x, y
        else:
            if y > y2:
                x, y, x2, y2 = x2, y2, x, y
        return x, y, x2, y2
    
    
    def __contains__(self, (x, y, x2, y2)):
        return self.normalise(x, y, x2, y2) in self.doors
    
    
    def add(self, x, y, x2, y2):
        self.doors.add(self.normalise(x, y, x2, y2))
    
    
    def remove(self, x, y, x2, y2):
        self.doors.remove(self.normalise(x, y, x2, y2))
    
    
    def __iter__(self):
        return iter(self.doors)
    