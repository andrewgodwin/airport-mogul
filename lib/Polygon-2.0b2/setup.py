#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       $Id: setup.py,v 1.34 2007/04/19 09:38:24 joerg Exp $    

# withNumPy enables some extensions:
#  * faster adding of contours from NumPy arrays
#  * data style STYLE_NUMPY to get contours and TriStrips
#    as NumPy arrays
withNumPy=False

# the include path for numpy/arrayobject.h
numPyIncludePath=''

# defaultStyle may be used to set the default style to one of:
#  * STYLE_TUPLE to get tuples of points
#  * STYLE_LIST to get lists of points
#  * STYLE_NUMPY to get points as NumPy array
#    withNumPy must be enabled for this!
defaultStyle='STYLE_LIST'

# ------ no changes below! If you need to change, it's a bug! -------
from distutils.core import setup, Extension
from sys import platform

mac = [('DEFAULT_STYLE', defaultStyle)]
inc = ['src']

if withNumPy:
    try:
        import numpy
        print "Using NumPy extension"
        mac.append(('WITH_NUMPY', 1))
    except:
        print "NumPy extension not found!"

# alloca() needs malloc.h under Windows
if platform == 'win32':
    mac.append(('SYSTEM_WIN32', 1))

if withNumPy and numPyIncludePath:
    inc.append(numPyIncludePath)

longdesc = """
Polygon is a python package for easy handling of polygons in 2D. It contains 
Python bindings for gpc, the excellent General Polygon Clipping Library by 
Alan Murta and some extensions written in C and pure Python. With Polygon you 
may handle complex polygonal areas in Python in a very intuitive way. Polygons 
are simple Python objects, clipping operations are bound to standard operators 
like +, -, \|, & and ^. TriStrips can be constructed from Polygons with a 
single statement. Functions to compute the area, center point, convex hull and 
much more are included.

The gpc homepage is located at http://www.cs.man.ac.uk/~toby/alan/software/ .

The wrapping and extension code is free software, but the core gpc library is
free for non-commercial usage only. The author says:

    GPC is free for non-commercial use only. We invite non-commercial users 
    to make a voluntary donation towards the upkeep of GPC.
    
    If you wish to use GPC in support of a commercial product, you must obtain 
    an official GPC Commercial Use Licence from The University of Manchester.

Please respect this statement and contact the author (see gpc homepage) if you
wish to use this software in commercial projects!
"""


args = { 
    'name'            : "Polygon",
    'version'         : "2.0b2",
    'description'     : "Polygon eases the handling of 2D-polygons including very fast clipping operations",
    'long_description': longdesc,
    'license'         : "LGPL for Polygon, other for gpc",
    'author'          : "Joerg Raedler",
    'author_email'    : "jr@j-raedler.de",
    'maintainer'      : "Joerg Raedler",
    'maintainer_email': "jr@j-raedler.de",
    'url'             : "http://polygon.origo.ethz.ch/",
    'download_url'    : "http://polygon.origo.ethz.ch/download",
    'classifiers'     : ['Development Status :: 5 - Production/Stable', 'Intended Audience :: Developers',
        'Intended Audience :: Science/Research', 'License :: Freely Distributable', 'License :: Other/Proprietary License',
        'Programming Language :: C', 'Programming Language :: Python', 'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Mathematics', 'Topic :: Scientific/Engineering :: Visualization'
    ],
    'packages'        : ['Polygon'],
    'ext_modules'     : [Extension('Polygon.cPolygon', ['src/gpc.c', 'src/cPolygon.c', 'src/PolyUtil.c'],
                        include_dirs=inc, define_macros=mac)]
}

setup(**args)
