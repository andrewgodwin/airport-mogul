
class Item(object):
    """
    Base class for an item - something that sits on the map, or in a room,
    and is rotateable.
    
    More than one Item per square is permitted, although each item has a
    'vertical occupancy list' - i.e., whether it uses the floor, the lower
    part of the square, and the upper part. A bench would use only the lower
    part, a control tower all three, a rug only the floor, etc. It's stored
    in the bit mask 'occupies', with 1=floor, 2=lower, 4=upper.
    
    Items also have Shapes; i.e. the pattern of floor tiles they occupy,
    respective to the origin. It's a list of relative coords, and must only
    have positive entries in it, and must include at least one tile on the zero
    line of each axis.
    """
    
    occupies = 7
    shape = [(0, 0)]
    
    @classmethod
    def from_defn(cls, defn):
        item = cls()
        item.model_name = defn['model']
        
    
    def size(self):
        "Returns the size of this item's bounding box"
        x1, y1 = self.shape[0]
        for x, y in self.shape:
            if x > x1:
                x1 = x
            if y > y1:
                y1 = y
        return x1+1, y1+1