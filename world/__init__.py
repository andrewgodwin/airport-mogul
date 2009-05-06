
from world.locdict import LocDict

class World(object):
    
    """
    Represents the overall world.
    """
    
    def __init__(self, (sizex, sizey)):
        
        self._expanses = {} # LocDicts, indexed by floor number
        self.size = (sizex, sizey)
    
    
    def add_expanse(self, expanse, coords):
        "Adds the given Expanse to the World."
        if expanse.floor not in self._expanses:
            self._expanses[expanse.floor] = LocDict()
        for x, y in coords:
            self._expanses[expanse.floor].add(x, y, expanse)
    
    
    def get_expanses(self, floor=None):
        if floor:
            for expanse in self._expanses[floor]:
                yield expanse
        else:
            for locdict in self._expanses.values():
                for expanse in locdict:
                    yield expanse
    
    
    def get_floor(self, floor):
        return self._expanses[floor]
    

def range2d(x, y, x2, y2):
    for ax in range(x, x2):
        for ay in range(y, y2):
            yield ax, ay


def build_test_world():
    
    from world.expanse import Expanse
    from world.room import Room
    
    world = World((1024, 1024))
    expanse = Expanse.from_coords(world, 0, range2d(1, 1, 9, 9))
    room = Room.from_coords(expanse, "corridor", range2d(3, 1, 9, 9))
    room = Room.from_coords(expanse, "lounge", range2d(1, 1, 3, 9))
    expanse.add_door(3, 2, 3, 3)
    
    print "Built test world."
    
    return world