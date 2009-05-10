"""
In-game controller and functions.
"""

from gui import BaseController
from world import build_test_world
from geometry import enlarge_polygon, enlarge_edge

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.task import Task

#This task runs for two seconds, then prints done
def exampleTask(task):
    if task.time < 2.0:
        return Task.cont
    print 'Done'
    return Task.done


def make_vertex_data(name="data"):
    "Creates a GeomVertexData and writers, ready for input"
    format = GeomVertexFormat.getV3c4t2()
    vdata = GeomVertexData(name, format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, 'vertex')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')
    return vdata, vertex, color, texcoord


class InGameController(BaseController):
    
    ZOOM_MULT = 0.1
    PAN_STEP = 0.01
    PAN_START = 0.003
    ROTATE_SPEED = 80
    
    ROOM_TEXTURES = {
        "corridor": ("wall_2.png", "floor_1.png"),
        "lounge": ("wall_2.png", "floor_2.png"),
    }
    
    def setup(self):
        
        self.world = build_test_world()
        self.root = render.attachNewNode("GameRoot")
        
        # Put the camera in a sensible place
        base.disableMouse()
        
        self.camera = render.attachNewNode("CameraOrigin")
        self.camera.setPos(2, 2, 0)
        self.camera.setHpr(-45, 0, 0)
        
        base.camera.reparentTo(self.camera)
        base.camera.setPos(0, -20, 20)
        base.camera.setHpr(0, -20, 0)
        base.camera.lookAt(self.camera)
        
        # Attach to mouse/keyb events
        self.accept("wheel_up", self.zoom_in)
        self.accept("wheel_down", self.zoom_out)
        
        self.accept("w", lambda: self.add_pan(0, 1))
        self.accept("w-up", lambda: self.add_pan(0, -1))
        
        self.accept("s", lambda: self.add_pan(0, -1))
        self.accept("s-up", lambda: self.add_pan(0, 1))
        
        self.accept("a", lambda: self.add_pan(-1, 0))
        self.accept("a-up", lambda: self.add_pan(1, 0))
        
        self.accept("d", lambda: self.add_pan(1, 0))
        self.accept("d-up", lambda: self.add_pan(-1, 0))
        
        self.accept("q", lambda: self.set_rotate(1))
        self.accept("q-up", lambda: self.set_rotate(0))
        
        self.accept("e", lambda: self.set_rotate(-1))
        self.accept("e-up", lambda: self.set_rotate(0))
        
        self.accept("mouse1", self.mouse1_pressed)
        
        self.prepare_mouse_picker()
        
        self.pan_dir = [0, 0]
        self.rotate_speed = 0
        
        # Set up game world
        self.create_base()
        self.create_outer_walls(self.world)
        for room in self.world.rooms:
            self.create_room(self.world, room)
        for item in self.world.items:
            self.create_item(self.world, item)
        
        # Add a test Person
        self.people = self.root.attachNewNode("People")
        person = PersonModel(self.people.attachNewNode("test_person"))
        person.set_position(3, 2.5, 0)
    
    
    def get_zoom(self):
        return base.camera.getDistance(self.camera)
    
    
    def zoom_in(self):
        "Zooms the camera in"
        base.camera.setPos(base.camera, 0, self.get_zoom()*self.ZOOM_MULT, 0)
    
    
    def zoom_out(self):
        "Zooms the camera out"
        base.camera.setPos(base.camera, 0, -self.get_zoom()*self.ZOOM_MULT, 0)

    
    def add_pan(self, x, y):
        "Starts or adds to a pan across the landscape."
        # See if we have started a pan
        if self.pan_dir == [0,0]:
            taskMgr.add(self.pan_task, 'PanTask')
        # Add our current delta to pan_dir
        self.pan_dir[0] += x
        self.pan_dir[1] += y
        # See if we have finished a pan
        if self.pan_dir == [0,0]:
            taskMgr.remove('PanTask')
    
    
    def pan_task(self, task):
        zoom = self.get_zoom()
        pan_speed = self.PAN_START + self.PAN_STEP * task.time
        self.camera.setPos(
            self.camera,
            self.pan_dir[0] * pan_speed * zoom,
            self.pan_dir[1] * pan_speed * zoom,
            0,
        )
        return Task.cont

    
    def set_rotate(self, r):
        "Allows setting of rotation speed for the camera."
        # See if we have started a rotate
        if self.rotate_speed == 0:
            taskMgr.add(self.rotate_task, 'RotateTask')
        # Add our current delta to rotate_speed
        self.rotate_speed = r
        self.rotate_origin = self.camera.getHpr()[0]
        # See if we have finished a rotate
        if self.rotate_speed == 0:
            taskMgr.remove('RotateTask')
    
    
    def rotate_task(self, task):
        self.camera.setHpr(
            self.rotate_origin + self.rotate_speed * task.time * self.ROTATE_SPEED,
            0,
            0,
        )
        return Task.cont

    
    def prepare_mouse_picker(self):
        self.pickerRay = CollisionRay()
        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNP.show()
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerNode.addSolid(self.pickerRay)        
        self.picker.addCollider(self.pickerNP, self.queue)
        self.picker.showCollisions(base.camera)

    
    def pick_from_coords(self, x, y):
        base.camera.ls()
        self.pickerRay.setFromLens(base.camNode, x, y)
        self.picker.traverse(render)
        if (self.queue.getNumEntries() > 0):
            self.queue.sortEntries()
            obj = self.queue.getEntry(0).getIntoNodePath()
            self.floorPosition = self.queue.getEntry(0).getSurfacePoint(obj)
    
    
    def mouse1_pressed(self):
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            print "Mouse at:", x, y
            self.pick_from_coords(x, y)
    
    
    def create_base(self):
        "Creates the base layer (i.e. a rectangle of grass)"
        # Make the VertexData
        vdata, vertex, color, texcoord = make_vertex_data("base_layer")
        for x, y in [(0,0), (self.world.size[0], 0), self.world.size, (0, self.world.size[1])]:
            vertex.addData3f(x, y, 0)
            color.addData4f(1, 1, 1, 1)
            texcoord.addData2f(x/2.0, y/2.0)
        # Now, make the plane
        prim = GeomTristrips(Geom.UHStatic)
        prim.addVertices(0, 1, 3, 2)
        prim.closePrimitive()
        # And add it to the scene
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode('base_layer')
        node.addGeom(geom)
        tex = loader.loadTexture('textures/grass.png', minfilter=Texture.FTLinearMipmapLinear)
        node_path = self.root.attachNewNode(node)
        node_path.setTexture(tex)
    
    
    def create_wall(self, item, locdict, doordict, inside=False, w=0.025, h=1):
        "Creates a wall along the boundar[y,ies] of the given item in the given locdict"
        # Set up the two drawing constructs
        vdata, vertex, color, texcoord = make_vertex_data("base_layer")
        prim = GeomTristrips(Geom.UHStatic)
        doors = set()
        draw_walls = [] # Two 2D points for the wall, one 2D vector for the width, one for the taper either end.
        # Outside walls don't have a particular item
        if inside:
            coords = locdict.coords_for_item(item)
            test = lambda x: x is item
        else:
            coords = item
            test = lambda x: x is not None
        # Loop through each coord...
        for x, y, z in coords:
            # Test to see which sides of this coord are exposed.
            if not test(locdict.get(x-1, y, z)):
                # Determine what kind of corners either end has
                c1 = not test(locdict.get(x, y-1, z))
                c2 = not test(locdict.get(x, y+1, z))
                ic1 = test(locdict.get(x-1, y-1, z))
                ic2 = test(locdict.get(x-1, y+1, z))
                # Correctly swap if we're doing an inside wall
                if inside:
                    wall = (x, y+1, x, y, z, w, 0)
                    c1, c2, ic1, ic2 = c2, c1, ic2, ic1
                else:
                    wall = (x, y, x, y+1, z, -w, 0)
                # Work out what kind of chamfer is needed
                chamfer = (0, -w if c1 else w if ic1 else 0, 0, w if c2 else -w if ic2 else 0)
                draw_walls.append(wall + chamfer)
            if not test(locdict.get(x+1, y, z)):
                # Determine what kind of corners either end has
                c1 = not test(locdict.get(x, y+1, z))
                c2 = not test(locdict.get(x, y-1, z))
                ic1 = test(locdict.get(x+1, y+1, z))
                ic2 = test(locdict.get(x+1, y-1, z))
                # Correctly swap if we're doing an inside wall
                if inside:
                    wall = (x+1, y, x+1, y+1, z, -w, 0)
                    c1, c2, ic1, ic2 = c2, c1, ic2, ic1
                else:
                    wall = (x+1, y+1, x+1, y, z, w, 0)
                # Work out what kind of chamfer is needed
                chamfer = (0, w if c1 else -w if ic1 else 0, 0, -w if c2 else w if ic2 else 0)
                draw_walls.append(wall + chamfer)
            if not test(locdict.get(x, y-1, z)):
                # Determine what kind of corners either end has
                c1 = not test(locdict.get(x+1, y, z))
                c2 = not test(locdict.get(x-1, y, z))
                ic1 = test(locdict.get(x+1, y-1, z))
                ic2 =  test(locdict.get(x-1, y-1, z))
                # Correctly swap if we're doing an inside wall
                if inside:
                    wall = (x, y, x+1, y, z, 0, w)
                    c1, c2, ic1, ic2 = c2, c1, ic2, ic1
                else:
                    wall = (x+1, y, x, y, z, 0, -w)
                # Work out what kind of chamfer is needed
                chamfer = (w if c1 else -w if ic1 else 0, 0, -w if c2 else w if ic2 else 0, 0)
                draw_walls.append(wall + chamfer)
            if not test(locdict.get(x, y+1, z)):
                # Determine what kind of corners either end has
                c1 = not test(locdict.get(x-1, y, z))
                c2 = not test(locdict.get(x+1, y, z))
                ic1 = test(locdict.get(x-1, y+1, z))
                ic2 = test(locdict.get(x+1, y+1, z))
                # Correctly swap if we're doing an inside wall
                if inside:
                    wall = (x+1, y+1, x, y+1, z, 0, -w)
                    c1, c2, ic1, ic2 = c2, c1, ic2, ic1
                else:
                    wall = (x, y+1, x+1, y+1, z, 0, w)
                # Work out what kind of chamfer is needed
                chamfer = (-w if c1 else w if ic1 else 0, 0, w if c2 else -w if ic2 else 0, 0)
                draw_walls.append(wall + chamfer)
        # For each wall in the lot we have to draw, make it.
        # (note: only one half of the wall is drawn; outer for expanses, inner for rooms)
        for x, y, x2, y2, z, dx, dy, t1x, t1y, t2x, t2y in draw_walls:
            # Work out the correct UV coords offset to get the textures straight
            if x2 != x:
                du1 = t1x / (x2 - x)
                du2 = t2x / (x2 - x)
            else:
                du1 = t1y / (y2 - y) 
                du2 = t2y / (y2 - y)
            # Is there a door on this wall?
            if (x, y, x2, y2, z) in doordict:
                ## Params ##
                dw = 0.8 # Width of door
                dh = 0.65 # Height of door
                ############
                ww = (1 - dw) * 0.5 # Width of one left/right wall segment
                x_bit = (x2 - x) * ww
                y_bit = (y2 - y) * ww
                points = [( # Right edge
                    (x+x_bit+dx, y+y_bit+dy, 0, 1-ww, 0),
                    (x+dx+t1x, y+dy+t1y, 0, 1-du1, 0),
                    (x+x_bit+dx, y+y_bit+dy, h, 1-ww, 0.9),
                    (x+dx+t1x, y+dy+t1y, h, 1-du1, 0.9),
                    (x+x_bit, y+y_bit, h, 1-ww, 1),
                    (x, y, h, 1, 1)
                ),( # Top section
                    (x2-x_bit+dx, y2-y_bit+dy, dh, ww, dh*0.9),
                    (x+x_bit+dx, y+y_bit+dy, dh, 1-ww, dh*0.9),
                    (x2-x_bit+dx, y2-y_bit+dy, h, ww, 0.9),
                    (x+x_bit+dx, y+y_bit+dy, h, 1-ww, 0.9),
                    (x2-x_bit, y2-y_bit, h, ww, 1),
                    (x+x_bit, y+y_bit, h, 1-ww, 1),
                ),( # Left edge
                    (x2+dx+t2x, y2+dy+t2y, 0, 0-du2, 0),
                    (x2-x_bit+dx, y2-y_bit+dy, 0, ww, 0),
                    (x2+dx+t2x, y2+dy+t2y, h, 0-du2, 0.9),
                    (x2-x_bit+dx, y2-y_bit+dy, h, ww, 0.9),
                    (x2, y2, h, 0, 1),
                    (x2-x_bit, y2-y_bit, h, ww, 1)
                )]
            else:
                points = [(
                    (x2+dx+t2x, y2+dy+t2y, 0, 0-du2, 0),
                    (x+dx+t1x, y+dy+t1y, 0, 1-du1, 0),
                    (x2+dx+t2x, y2+dy+t2y, h, 0-du2, 0.9),
                    (x+dx+t1x, y+dy+t1y, h, 1-du1, 0.9),
                    (x2, y2, h, 0, 1),
                    (x, y, h, 1, 1)
                )]
            # Draw the tristrip for the wall and its top
            for strip in points:
                for x, y, z, tx, ty in strip:
                    vertex.addData3f(x, y, z)
                    color.addData4f(1, 1, 1, 1)
                    texcoord.addData2f(tx, ty)
                prim.addNextVertices(len(strip)) 
                prim.closePrimitive()
        # Make a Geom and return
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        return geom
    
    
    def create_doors(self, root, doors):
        "Adds in the door models (they're premade, rather than generated)."
        door_root = root.attachNewNode("DoorRoot")
        for x, y, x2, y2, z in doors:
            if x == x2:
                rot = 90
            else:
                rot = 0
            door_nodepath = loader.loadModel("doors/door_1")
            door_nodepath.reparentTo(door_root)
            door_nodepath.setPos(x, y, 0)
            door_nodepath.setHpr(rot, 0, 0)
        return door_root

    
    def create_floor(self, item, locdict):
        """Makes a floor for the given item"""
        vdata, vertex, color, texcoord = make_vertex_data("polygon")
        prim = GeomTristrips(Geom.UHStatic)
        # Add each tile
        for x, y, z in locdict.coords_for_item(item):
            for x, y, tx, ty in (
                    (x, y+1, 0, 1),
                    (x, y, 0, 0),
                    (x+1, y+1, 1, 1),
                    (x+1, y, 1, 0),
                ):
                vertex.addData3f(x, y, z)
                color.addData4f(1, 1, 1, 1)
                texcoord.addData2f(tx, ty)
            prim.addNextVertices(4) 
            prim.closePrimitive()
        # Make a Geom and return
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        return geom
    
    
    def create_outer_walls(self, world):
        "Creates the model for an Expanse (i.e. outer walls; floors come from Rooms)."
        # Make a geom for the walls
        geom = self.create_wall(world.rooms.all_coords(), world.rooms, world.doors)
        wall_node = GeomNode('walls')
        wall_node.addGeom(geom)
        # Add a nodepath 'n' texture
        root = self.root.attachNewNode("expanse")
        wall_nodepath = root.attachNewNode(wall_node)
        tex = loader.loadTexture('textures/wall_1.png')
        wall_nodepath.setTexture(tex)
        return root
    
    
    def create_room(self, world, room):
        "Creates the model for an Room (i.e. inner walls and a floor)."
        # Make a geom for the walls
        geom = self.create_wall(room, world.rooms, world.doors, inside=True)
        wall_node = GeomNode('walls')
        wall_node.addGeom(geom)
        # And one for the floor
        geom = self.create_floor(room, world.rooms)
        floor_node = GeomNode('floor')
        floor_node.addGeom(geom)
        # Attach and combine
        root = self.root.attachNewNode("expanse")
        wall_nodepath = root.attachNewNode(wall_node)
        tex = loader.loadTexture(self.ROOM_TEXTURES[room.type][0])
        wall_nodepath.setTexture(tex)
        floor_nodepath = root.attachNewNode(floor_node)
        floor_nodepath.setPos(0, 0, 0.05)
        tex = loader.loadTexture(self.ROOM_TEXTURES[room.type][1])
        floor_nodepath.setTexture(tex)
        # Load on the door models
        self.create_doors(root, world.doors)
    
    
    def create_item(self, world, item):
        "Creates a node for an Item and sticks a model in it."
        # Make a new node for the item
        item_root = self.root.attachNewNode(item.name)
        item_root.setPos(*item.origin)
        # Load a model, add it
        model = loader.loadModel("items/%s" % item.model)
        model.reparentTo(item_root)


class PersonModel(object):
    
    """
    Represents the onscreen instance of a Person.
    """
    
    def __init__(self, nodepath):
        self.nodepath = nodepath
        self.load_model()
    
    def load_model(self):
        model = loader.loadModel("people/person_test")
        model.reparentTo(self.nodepath)
    
    def set_position(self, x, y, z):
        self.nodepath.setPos(x, y, z)
    