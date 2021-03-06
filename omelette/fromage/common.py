from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QGraphicsItem, QFont

class Drawable(object):
    """
    Base for other Drawable objects.
    Holds uml_object and list of anchors which are in slot relation with it.
    """


    def __init__(self, uml_object):
        self.uml_object = uml_object
        self.anchors = []

    """
    Crops QLineF, used mainly in relation to properly draw line 
    from one object to another. line_point is 0 when line.p1() is inside
    of the drawable, everything else when line.p2() inside. 
    
    This method shall be overloaded in specific drawables.  
    """
    def crop_line(self, line, line_point):
        return line
    
    def get_neighbours(self):
        return map(self.__get_other, self.anchors)
    
    def __get_other(self, anchor):
        link = anchor.connector
        if link.source_anchor.slot == self:
            return link.target_anchor.slot
        else:
            return link.source_anchor.slot

    """
    Returns boundingRect in relation to the diagram. Doesn't work if
    Drawable doesn't derive from QGraphicsItem (no boundingRect()).
    """
    #TODO: See if PyQt provides such functionality
    #TODO: Seems like QRectF QGraphicsItem.sceneBoundingRect (self) does that
    def globalBoundingRect(self):
        global_rect = QRectF(self.boundingRect())
        global_rect.translate(self.pos())

        return global_rect
    
    def globalFullBoundingRect(self):
        full_rect = QRectF(self.childrenBoundingRect() | self.boundingRect())
        full_rect.translate(self.pos())
        
        return full_rect
    
    def resize_scene_rect(self):
        # Check if we are QGraphicsItem and if we are on scene
        if(not callable(self.scene) or self.scene() == None): 
            return
        
        # TODO: A place for optimization?
        rect = QRectF(self.scene().sceneRect())
        self.scene().setSceneRect(rect.united(self.globalBoundingRect()))

    neighbours = property(get_neighbours)
    
    # Why not.
    @staticmethod
    def get_font():
        return QFont('Helvetica', 10)

class DrawableEdge(Drawable):
    """Base class for edgy things (e.g. lines, relations)."""

    def __init__(self, uml_object):
        super(DrawableEdge, self).__init__(uml_object)

        self.source_anchor = None
        self.target_anchor = None


class DrawableNode(Drawable):
    """Base class for node-like diagram elements (e.g. classes, use cases)."""

    def __init__(self, uml_object):
        super(DrawableNode, self).__init__(uml_object)


class Anchor(object):
    """
    Class representing connection between edge (connector) and something else
    (slot).
    """

    def __init__(self):
        self.connector = None
        self.slot = None
