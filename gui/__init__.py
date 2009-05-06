"""
Main game engine file.
"""

import os
from ConfigParser import SafeConfigParser

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class Gui(DirectObject):

    """
    Base class for the GUI; contains initialisation and utility methods
    for the graphics, and handles passing off to controllers.
    """

    def __init__(self):
        DirectObject.__init__(self)
        self.setup_panda()
        self.test_launch()


    def setup_panda(self):
        "Initialises the Panda3D parts."
        
        # Tell Panda we really want to use our own data dirs.
        self.dataPath = os.path.join(os.path.dirname(__file__), "..", "data")
        loadPrcFileData("", "model-path %s" % self.dataPath)
        loadPrcFileData("", "model-path %s/mesh/" % self.dataPath)
        loadPrcFileData("", "model-path %s/textures/" % self.dataPath)
        loadPrcFileData("", "texture-path %s/textures/" % self.dataPath)
        loadPrcFileData("", "texture-path %s/gui/" % self.dataPath)
        
        # Make that basic window a bit better.
        base.setBackgroundColor(0,0,0)
        base.enableParticles()
        
        # Create the pixel-perfect nodes
        self.addPixelNodes()
        self.accept("aspectRatioChanged", self.scalePixelNodes)
    
    
    def test_launch(self):
        from gui.ingame import InGameController
        InGameController(self)


    def start(self):
        "Enters the main loop."
        run()


    def addPixelNodes(self):
        """
	Adds some nodes that will always expose a 1:1 scale with screen pixels.
	"""

        # A few that are pixel-perfect vertically but stretch horizontally.
        self.p2dts = aspect2d.find("**/a2dTopCenter").attachNewNode("p2dts")
        self.p2dcs = render2d.attachNewNode("p2dcs")
        self.p2dbs = aspect2d.find("**/a2dBottomCenter").attachNewNode("p2dns")

        # We create pixel-perfect nodes
        self.p2dbl = aspect2d.find("**/a2dBottomLeft").attachNewNode("p2dbl")
        self.p2dbc = aspect2d.find("**/a2dBottomCenter").attachNewNode("p2dbc")
        self.p2dbr = aspect2d.find("**/a2dBottomRight").attachNewNode("p2dbr")
        self.p2dtl = aspect2d.find("**/a2dTopLeft").attachNewNode("p2dtl")
        self.p2dtc = aspect2d.find("**/a2dTopCenter").attachNewNode("p2dtc")
        self.p2dtr = aspect2d.find("**/a2dTopRight").attachNewNode("p2dtr")
        self.p2dcl = aspect2d.find("**/a2dLeftCenter").attachNewNode("p2dcl")
        self.p2dcc = aspect2d.attachNewNode("p2dcc")
        self.p2dcr = aspect2d.find("**/a2dRightCenter").attachNewNode("p2dcr")

        self.scalePixelNodes()


    def scalePixelNodes(self):
        """
	Resizes the pixel nodes based on the screen, so they remain at a scale
	of 1:1 pixel. Called whenever the window is resized.
	"""

        screenw = base.win.getXSize()
        screenh = base.win.getYSize()

        for p2node in [self.p2dbl, self.p2dbr, self.p2dtl, self.p2dtr, \
                       self.p2dtc, self.p2dbc, self.p2dcl, self.p2dcc, self.p2dcr]:
            p2node.setScale(render2d, 2.0/screenw, 1, 2.0/screenh)

        for p2node in [self.p2dts, self.p2dcs, self.p2dbs]:
            p2node.setScale(render2d, 1, 1, 2.0/screenh)



class BaseController(DirectObject):

    """
    Superclass for all gui creator/controllers.
    Provides some useful functions.
    """

    def __init__(self, gui, *args, **kwds):
        DirectObject.__init__(self)
        self.gui = gui
        self.cleanable = []
        self.setup(*args, **kwds)


    def setup(self):
        "Should be overridden with the actual setup code for the scene/menu."
        pass


    def clean(self):
        "Deletes stuff we added to the scene graph."
        for name in self.cleanable:
            getattr(self, name).removeNode()
            delattr(self, name)
        self.cleanable = []
        self.ignoreAll()


    def turnInto(self, cls, *args, **kwds):
        "Hands over to the given class; cleans up first."
        self.clean()
        cls(self.app, *args, **kwds)