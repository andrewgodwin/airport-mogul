
from Polygon import Polygon
from world.locdict import ItemDict

class Room(object):
    
    """
    A room inside an Expanse.
    """
    
    def __init__(self, expanse, type):
        self.expanse = expanse
        self.type = type
        self.items = ItemDict()
    
    @classmethod
    def from_coords(cls, expanse, type, coords):
        instance = cls(expanse, type)
        expanse.add_room(instance, coords)
        return instance