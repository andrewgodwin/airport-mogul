# -*- coding: utf-8 -*-
#       $Id: Polygon.py,v 1.27 2006/04/19 09:41:12 joerg Exp $  

from cPolygon import Polygon
from math import sqrt, fabs
from operator import add


def fillHoles(poly):
    """
    Returns the polygon p without any holes.

    :Arguments:
        - p: Polygon
    :Returns:
        new Polygon
    """
    n = Polygon()
    [n.addContour(poly[i]) for i in range(len(poly)) if poly.isSolid(i)]
    return n


def pointList(poly, withHoles=1):
    """
    Returns a list of all points of p.

    :Arguments:
        - p: Polygon
    :Returns:
        list of points
    """
    if not withHoles:
        poly = fillHoles(poly)
    return reduce(add, [list(c) for c in poly])


__left = lambda p: (p[1][0]*p[2][1]+p[0][0]*p[1][1]+p[2][0]*p[0][1]-
                    p[1][0]*p[0][1]-p[2][0]*p[1][1]-p[0][0]*p[2][1] >= 0)
def convexHull(poly):
    """
    Returns a polygon which is the convex hull of p.

    :Arguments:
        - p: Polygon
    :Returns:
        new Polygon
    """
    points = list(pointList(poly, 0))
    points.sort()
    u = [points[0], points[1]]
    for p in points[2:]:
        u.append(p)
        while len(u) > 2 and __left(u[-3:]):
            del u[-2]
    points.reverse()
    l = [points[0], points[1]]
    for p in points[2:]:
        l.append(p)
        while len(l) > 2 and __left(l[-3:]):
            del l[-2]
    return Polygon(u+l[1:-1])


def tile(poly, x=[], y=[], bb=None):
    """
    Returns a list of polygons which are tiles of p splitted at the border values 
    specified in x and y. If you already know the bounding box of p, you may give 
    it as argument bb (4-tuple) to speed up the calculation.

    :Arguments:
        - p: Polygon
        - x: list of floats
        - y: list of floats
        - optional bb: tuple of 4 floats
    :Returns:
        list of new Polygons
    """
    if not (x or y):
        return [poly] # nothin' to do
    bb = bb or poly.boundingBox()
    x = [bb[0]] + [i for i in x if bb[0] < i < bb[1]] + [bb[1]]
    y = [bb[2]] + [j for j in y if bb[2] < j < bb[3]] + [bb[3]]
    x.sort()
    y.sort()
    cutpoly = []
    for i in range(len(x)-1):
        for j in range(len(y)-1):
            cutpoly.append(Polygon(((x[i],y[j]),(x[i],y[j+1]),(x[i+1],y[j+1]),(x[i+1],y[j]))))
    tmp = [c & poly for c in cutpoly]
    return [p for p in tmp if p]


def tileEqual(poly, nx=1, ny=1, bb=None):
    """
    works like tile(), but splits into nx and ny parts.

    :Arguments:
        - p: Polygon
        - nx: integer
        - ny: integer
        - optional bb: tuple of 4 floats
    :Returns:
        list of new Polygons
    """
    bb = bb or poly.boundingBox()
    s0, s1 = bb[0], bb[2]
    a0, a1 = (bb[1]-bb[0])/nx, (bb[3]-bb[2])/ny 
    return tile(poly, [s0+a0*i for i in range(1, nx)], [s1+a1*i for i in range(1, ny)], bb)


def warpToOrigin(poly):
    """
    Shifts lower left corner of the bounding box to origin.

    :Arguments:
        - p: Polygon
    :Returns:
        None
    """
    x0, x1, y0, y1 = poly.boundingBox()
    poly.shift(-x0, -y0)


def centerAroundOrigin(poly):
    """
    Shifts the center of the bounding box to origin.

    :Arguments:
        - p: Polygon
    :Returns:
        None
    """
    x0, x1, y0, y1 = poly.boundingBox()
    poly.shift(-0.5(x0+x1), -0.5*(yo+y1))


__vImp = lambda p: ((sqrt((p[1][0]-p[0][0])**2 + (p[1][1]-p[0][1])**2) +
                     sqrt((p[2][0]-p[1][0])**2 + (p[2][1]-p[1][1])**2)) *
                    fabs(p[1][0]*p[2][1]+p[0][0]*p[1][1]+p[2][0]*p[0][1]-
                              p[1][0]*p[0][1]-p[2][0]*p[1][1]-p[0][0]*p[2][1]))
def reducePoints(cont, n):
    """
    Remove points of the contour 'cont', return a new contour with 'n' points.
    *Very simple* approach to reduce the number of points of a contour. Each point 
    gets an associated 'value of importance' which is the product of the lengths 
    and absolute angle of the left and right vertex. The points are sorted by this 
    value and the n most important points are returned. This method may give 
    *very* bad results for some contours like symmetric figures. It may even 
    produce self-intersecting contours which are not valid to process with 
    this module.

    :Arguments:
        - contour: list of points
    :Returns:
        new list of points
    """
    if n >= len(cont):
        return cont
    cont = list(cont)
    cont.insert(0, cont[-1])
    cont.append(cont[1])
    a = [(__vImp(cont[i-1:i+2]), i) for i in range(1, len(cont)-1)]
    a.sort()
    ind = [x[1] for x in a[len(cont)-n-2:]]
    ind.sort()
    return [cont[i] for i in ind]


__linVal = lambda p: (p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[1][1]-p[0][1])*(p[2][0]-p[0][0])
def prunePoints(poly):
    """
    Returns a new Polygon which has exactly the same shape as p, but unneeded 
    points are removed. The new Polygon has no double points or points that are 
    exactly on a straight line.

    :Arguments:
        - p: Polygon
    :Returns:
        new Polygon
    """
    np = Polygon()
    for x in range(len(poly)): # loop over contours
        c = list(poly[x])
        c.insert(0, c[-1])
        c.append(c[1])
        # remove double points
        i = 1
        while (i < (len(c))):
            if c[i] == c[i-1]:
                del c[i]
            else:
                i += 1
        # remove points that are on a straight line
        n = []
        for i in range(1, len(c)-1):
            if __linVal(c[i-1:i+2]) != 0.0:
                n.append(c[i])
        if len(n) > 2:
            np.addContour(n, poly.isHole(x))
    return np
                

def cloneGrid(poly, con, xl, yl, xstep, ystep):
    """
    Create a single new polygon with contours that are made from contour con from 
    polygon poly arranged in a xl-yl-grid with spacing xstep and ystep.

    :Arguments:
        - poly: Polygon
        - con: integer
        - xl: integer
        - yl: integer
        - xstep: float
        - ystep: float
    :Returns:
        new Polygon
    """
    p = Polygon(poly[con])
    for xi in range(xl):
        for yi in range(yl):
            p.cloneContour(0, xi*xstep, yi*ystep)
    return p
