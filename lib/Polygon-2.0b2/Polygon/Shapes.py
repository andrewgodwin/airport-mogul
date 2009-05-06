# -*- coding: utf-8 -*-
#       $Id: Polygon.py,v 1.27 2006/04/19 09:41:12 joerg Exp $  

from cPolygon import Polygon
from math import sin, cos, pi


def Circle(radius=1.0, center=(0.0,0.0), points=32):
    """
    Create a polygonal approximation of a circle.

    :Arguments:
        - optional radius: float
        - optional center: point (2-tuple of float)
        - optional points: integer
    :Returns:
        new Polygon
    """
    p = []
    for i in range(points):
        a = 2.0*pi*float(i)/points
        p.append((center[0]+radius*sin(a), center[1]+radius*cos(a)))
    return Polygon(p)


def Star(radius=1.0, center=(0.0,0.0), beams=16, iradius=0.5):
    """
    Create a star shape, iradius is the inner and radius the outer radius.

    :Arguments:
        - optional radius: float
        - optional center: point (2-tuple of float)
        - optional beams: integer
        - optional iradius: float
    :Returns:
        new Polygon
    """
    p = []
    for i in range(beams):
        a = 2.0*pi*float(i)/beams
        p.append((center[0]+radius*sin(a), center[1]+radius*cos(a)))
        b = 2.0*pi*(float(i)+0.5)/beams
        p.append((center[0]+iradius*sin(b), center[1]+iradius*cos(b)))
    return Polygon(p)


def Rectangle(xl= 1.0, yl=None):
    """
    Create a rectangular shape. If yl is not set, a square is created.

    :Arguments:
        - optional xl: float
        - optional yl: float
    :Returns:
        new Polygon
    """
    if yl is None: yl = xl
    return Polygon(((0.0, 0.0), (xl, 0.0), (xl, yl), (0.0, yl)))
