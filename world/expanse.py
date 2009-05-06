
from Polygon import Polygon
from world.locdict import LocDict, DoorDict

class Expanse(object):
    
    """
    A building floor, a single contiguous set of tiles, on a certain floor.
    The tiles it covers is managed by the World.
    """
    
    def __init__(self, world, floor):
        self.world = world
        self.floor = floor
        self.rooms = LocDict()
        self.doors = DoorDict()
    
    @classmethod
    def from_coords(cls, world, floor, coords):
        instance = cls(world, floor)
        world.add_expanse(instance, coords)
        return instance
    
    def add_room(self, room, coords):
        "Adds the Room to this Expanse."
        for x, y in coords:
            self.rooms.add(x, y, room)
    
    def add_door(self, x, y, x2, y2):
        "Adds a Door along the given wall."
        self.doors.add(x, y, x2, y2)
    
    def __iter__(self):
        return iter(self.rooms)