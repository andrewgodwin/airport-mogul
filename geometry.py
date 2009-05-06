"""
General helpful geometry functions.
"""

import math
import datetime
import random

from Polygon import Polygon
from Polygon.Utils import fillHoles


######################################################## Vectors (2D) ##########

class Vector(object):
    
    def __init__(self, x, y=None):
        if y == None:
            if len(x) == 2:
                self.x, self.y = x
            else:
                raise ValueError("Please pass either a tuple of (x, y) or two parameters.")
        else:
            self.x = x
            self.y = y
    
    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y)
    
    def __mul__(self, num):
        return Vector(self.x*num, self.y*num)
    
    def __div__(self, num):
        return self * (1.0 / num)
    
    def dot(self, other):
        return self.x*other.x + self.y*other.y
    
    def __len__(self):
        return abs(self)
    
    def __abs__(self):
        return (self.x**2 + self.y**2)**0.5

    def normalise(self):
        if self.x == 0 and self.y == 0:
            return self
        return self / abs(self)
    
    def tuple(self):
        return self.x, self.y
    
    def __repr__(self):
        return "<%s,%s>" % (self.x, self.y)
    
    def swap(self):
        return Vector(self.y, self.x)
    
    def rotate(self, angle):
        return Vector(
            math.cos(angle)*self.x - math.sin(angle)*self.y,
            math.sin(angle)*self.x + math.cos(angle)*self.y,
        )
    
    def samedir(self, other):
        if self.dot(other) < 0:
            return self * -1
        else:
            return self

RIGHT_ANGLE = math.pi / 2

######################################################## Exceptions ############


class NothingFound(Exception):
    pass


######################################################## Polygon functions #####


def wrap_line_intersects_poly(*a, **k):
    return intersect.line_intersects_poly(*a, **k)


def nearest_corner(poly, x, y, n=1):
    points = [(cx, cy, ((cx-x)**2+(cy-y)**2)**0.5, i) for i, (cx, cy) in enumerate(poly[0])]
    points.sort(key=lambda (x,y,d,i): d)
    if n == 1:
        return points[0]
    else:
        return points[:n]

    
def vector_to_edge(point, end1, end2):
    "Returns the shortest vector from this line segment to the given point."
    perp = (end1 - end2).rotate(math.pi/2.0)
    
    # Proj onto line to see if it's inside the segment
    lpos = abs((end1-end2).dot(end1-point))
    if lpos < 0:
        # It's before end1
        return end1-point
    elif lpos > 1:
        # It's after end2
        return end2-point
    else:
        # It's along the segment
        return (end1-end2)*lpos - point
    

def vector_to_poly(point, poly):
    points = map(Vector, poly[0])
    if poly.isInside(*point.tuple()):
        return 0
    # TODO: More reliable test?
    lowest_distance = None
    for e1, e2 in zip(points, points[1:]+points[:1]):
        v = vector_to_edge(point, e1, e2)
        if lowest_distance is None or lowest_distance[0] > abs(v):
            lowest_distance = abs(v), v
    return lowest_distance[1]
    

def angle_between(v1, v2):
    v1n = v1.normalise()
    v2n = v2.normalise()
    t = v1n.dot(v2n)
    if t > 1:
        return 0
    return math.acos(t)


def enlarge_polygon(poly, r, accuracy=3, inside_override=None):
    "cspace-enlarges the given polygon by r"
    plist = points = [Vector(x, y) for x, y in poly[0]]
    plist = list(enumerate(points))
    newpoints = []
    np = len(points)
    # If an inside/outside (i.e. cw/anticw) is specified, ignore the endpoints
    if inside_override is not None:
        plist = plist[1:-1]
    for i, point in plist:
        # Get the neighbour points
        next = points[(i+1) % np]
        prev = points[(i-1) % np]
        
        # Get the edge normals
        e1 = (prev - point).rotate(RIGHT_ANGLE).normalise()
        mid1 = (prev+point)/2
        e2 = (next - point).rotate(-RIGHT_ANGLE).normalise()
        mid2 = (next+point)/2
        
        # If they're pointing "inside" the polygon, rotate them.
        if inside_override is not None:
            points_inside = inside_override
        else:
            points_inside = poly.isInside(*(e1*0.001+mid1).tuple())
        if points_inside:
            e1 *= -1
            e2 *= -1
        
        # Work out the angle between the two sides
        angle = angle_between(e1, e2)
        
        # Average the normals to get the 'vertex normal'
        norm = ((e1 + e2) / 2.0).normalise()
        
        # If they're pointing towards each other then 
        # the dotproduct of e1 and (mid2 - mid1) should be positive
        mdot = e1.dot(mid2 - mid1)
        # Use that to see if the corner is inner or outer
        if accuracy < 0 or mdot >= 0:
            # Inner
            inner_angle = angle_between((prev-point),(next-point)) / 2
            if inner_angle == 0:
                newpoints.append(point + (norm * r))
            else:
                newpoints.append(point + (norm * (r/math.sin(inner_angle))))
        else:
            # Outer
            # If moving along the angle increases the angle between e1 and
            # the vertex normal then reverse it
            if angle_between(e1.rotate(angle/2), norm) > angle_between(e1, norm):
                angle *= -1
            angle_part = angle / float(accuracy+1)
            if angle_part == 0:
                continue
            current_angle = 0
            while abs(current_angle) <= abs(angle):
                newpoints.append(point + (e1 * r).rotate(current_angle))
                current_angle += angle_part
    # Return new polygon
    return Polygon([p.tuple() for p in newpoints])


def enlarge_edge(poly, r, accuracy=3):
    "Like enlarge_polygon, but for open polygons."
    points = [Vector(x, y) for x, y in poly[0]]
    side1 = []
    side2 = []
    np = len(points)
    if np > 2:
        # For both sides, generate them
        side1 = enlarge_polygon(poly, r, accuracy, True)[0]
        side2 = enlarge_polygon(poly, r, accuracy, False)[0]
        side2.reverse()
    # Generate the endcaps
    e1 = (points[1] - points[0]).rotate(RIGHT_ANGLE).normalise() * -r
    e2 = (points[-2] - points[-1]).rotate(RIGHT_ANGLE).normalise()
    end1 = []
    end2 = []
    if accuracy < 0:
        # Use square caps
        end1.append((points[0] + e1 + e1.rotate(-RIGHT_ANGLE)).tuple())
        end1.append((points[0] - e1 + e1.rotate(-RIGHT_ANGLE)).tuple())
        end2.append((points[-1] - e2 + e2.rotate(RIGHT_ANGLE)).tuple())
        end2.append((points[-1] + e2 + e2.rotate(RIGHT_ANGLE)).tuple())
    else:
        # Use round caps
        num = float((accuracy * 2) + 1)
        for i in range(int(num+1)):
            end1.append((points[0] + e1.rotate(-RIGHT_ANGLE*2*i/num)).tuple())
        for i in range(int(num+1)):
            end2.append((points[-1] + e2.rotate(-RIGHT_ANGLE*2*i/num)*-1).tuple())
    newpoints = end1 + side1 + end2 + side2
    # Smoosh those two together
    return Polygon(newpoints)