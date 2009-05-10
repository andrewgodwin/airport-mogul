
from world.locdict import LocDict, ItemDict, DoorDict
from world.constants import *

class World(object):
    
    """
    Represents the overall world.
    """
    
    def __init__(self, (sizex, sizey)):
        
        self.rooms = LocDict()
        self.doors = DoorDict()
        self.items = ItemDict()
        self.size = (sizex, sizey)
    
    
    def add_room(self, room, coords):
        "Adds the given Expanse to the World."
        for x, y, z in coords:
            self.rooms.add(x, y, z, room)
    
    
    def add_door(self, x1, y1, x2, y2, z):
        self.doors.add(x1, y1, x2, y2, z)
    
    
    def add_item(self, item, x, y, z, rot):
        self.items.add(x, y, z, rot, item)
    
    
    

def range2d(x, y, x2, y2, z):
    for ax in range(x, x2):
        for ay in range(y, y2):
            yield ax, ay, z


def build_test_world():
    
    from world.room import Room
    from world.item import Item
    
    world = World((1024, 1024))
    room = Room.from_coords(world, "corridor", range2d(3, 1, 9, 9, 0))
    room = Room.from_coords(world, "lounge", range2d(1, 1, 3, 9, 0))
    world.add_door(3, 2, 3, 3, 0)
    
    item = Item("departures-board", "Departures Board", "screens", USES_NONFLOOR)
    world.add_item(item, 5, 5, 0, 0)
    
    print "Built test world."
    
    return world