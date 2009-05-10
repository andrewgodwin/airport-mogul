
class LocDict(object):
    
    """
    A 'location dictionary', i.e. one that contains items referenced by location
    (their sets of covered squares). Should probably be a set of quadtrees.
    """
    
    def __init__(self):
        
        self._grids = {}
        self._items = {}
        self._sizes = {}
    
    
    def grow_to_size(self, width, height, z):
        "Increases the size of the items grid to the given size."
        
        # Make sure there's a level at z
        if z not in self._grids:
            self._grids[z] = []
            self._sizes[z] = [0, 0]
        # Extend it in the x direction
        if width > self._sizes[z][0]:
            self._grids[z].extend([[None] * max(height, self._sizes[z][1]) for i in range(width - len(self._grids[z]))])
            self._sizes[z][0] = width
        # And the y direction
        if height > self._sizes[z][1]:
            for column in self._grids[z]:
                column.extend([None] * (height - len(column)))
            self._sizes[z][1] = height
    
    
    def add(self, x, y, z, item):
        "Adds an item to the LocDict at the given coords."
        # Make sure we're big enough.
        self.grow_to_size(x+1, y+1, z)
        # Remove anything previously there
        self.clear(x, y, z)
        # Add it to the grid and list of items.
        self._grids[z][x][y] = item
        if item not in self._items:
            self._items[item] = [(x, y, z)]
        else:
            self._items[item].append((x, y, z))
    
    
    def clear(self, x, y, z):
        "Removes whatever was at x, y, z."
        item = self._grids[z][x][y]
        if item is not None:
            self._grids[z][x][y] = None
            self._items[item].remove((x, y, z))
            if not self._items[item]:
                del self._items[item]
    
    
    def get(self, x, y, z):
        "Returns the item at (x, y, z)"
        try:
            return self._grids[z][x][y]
        except IndexError:
            return None
    
    
    def __iter__(self):
        return iter(self._items)
    
    
    def items(self):
        return self._items.items()
    
    
    def coords_for_item(self, item):
        return self._items[item]
    
    
    def all_coords(self):
        for item, coords in self._items.items():
            for coord in coords:
                yield coord



class ItemDict(LocDict):
    
    """
    A subclass of LocDict that tracks items - things with predefined floor
    patterns. Each Item has a .shape attribute which gives which squares
    it occupies relative to the origin and rotation.
    """
    
    def __init__(self):
        
        LocDict.__init__(self)
    
    
    def add(self, x, y, z, rot, item):
        """
        Adds the item at x,y with rotation rot (one of 0, 1, 2, 3 - number
        of 90deg rotations anticlockwise.)
        """
        # Remove it if it's already here
        if item in self._items:
            self.remove(item)
        # First, grow to fit it
        w, h = item.size()
        if rot % 2:
            w, h = h, w
        self.grow_to_size(x+w, y+h, z)
        # Then, add it to the squares
        squares = []
        for dx, dy in item.shape:
            nx, ny = dx+x, dy+y
            squares.append((nx, ny, z))
            # Make sure it's a set
            if self._grids[z][nx][ny] is None:
                self._grids[z][nx][ny] = set()
            # Stick it into the set
            self._grids[z][nx][ny].add(item)
        self._items = {item: squares}
        item.origin = (x, y, z)
        item.rotation = 90.0 * rot
    
    
    def remove(self, item):
        """
        Removes an item from the ItemDict.
        """
        for x, y, z in self._items[item]:
            self._grids[z][x][y].remove(item)
        del self._items[item]


    
class DoorDict(object):
    
    "Stores a set of 'doors' (i.e. wall segments - (1,2) to (2,2))"
    
    def __init__(self):
        self.doors = set()
    
    
    def normalise(self, x, y, x2, y2, z):
        "Ensures coordinates are always in a consistent order."
        if x > x2:
            x, y, x2, y2 = x2, y2, x, y
        else:
            if y > y2:
                x, y, x2, y2 = x2, y2, x, y
        return x, y, x2, y2, z
    
    
    def __contains__(self, (x, y, x2, y2, z)):
        return self.normalise(x, y, x2, y2, z) in self.doors
    
    
    def add(self, x, y, x2, y2, z):
        self.doors.add(self.normalise(x, y, x2, y2, z))
    
    
    def remove(self, x, y, x2, y2, z):
        self.doors.remove(self.normalise(x, y, x2, y2, z))
    
    
    def __iter__(self):
        return iter(self.doors)
    