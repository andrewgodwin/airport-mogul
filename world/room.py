
from Polygon import Polygon
from world.locdict import ItemDict

class Room(object):
    
    """
    A room inside an Expanse.
    """
    
    def __init__(self, expanse, type):
        self.expanse = expanse
        self.type = type
    
    @classmethod
    def from_coords(cls, world, type, coords):
        instance = cls(world, type)
        world.add_room(instance, coords)
        return instance