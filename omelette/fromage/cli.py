#!/usr/bin/env python
import sys
import os

script_path = os.path.dirname(os.path.realpath(__file__))
modules_path = os.path.normcase("../../")
modules_directory = os.path.join(script_path, modules_path)
sys.path.append(modules_directory)

import getopt
from PyQt4 import QtGui
from PyQt4.QtGui import QImage, QPainter, QGraphicsScene, QBrush, QColor
from PyQt4.Qt import *

from omelette.fromage.diagram import Diagram
from omelette.compiler.compiler import Compiler
from omelette.compiler.code import Code, Library
from omelette.fromage.layouter import Layouter
from omelette.compiler import logging

QT_APP = QtGui.QApplication([])

def usage():
    print "Usage: cli.py -h --help -i --input -o -output"

def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hi:o:", ["help", "input=", "output="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        return 1

    input = ""
    output = ""
    for o, a in opts:
        print o + " " + a
        if o in ("-h", "--help"):
            usage()
            return 0
        elif o in ("-i", "--input"):
            input = a
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unhandled opt"

    if(input == ""):
        input_file = sys.stdin
    else:
        try:
            input_file = open(input, 'r')
        except IOError, err:
            print "IOError: " + str(err)
            return 2
    code = Code(input_file.read())

    diagram = Diagram()
    scene = QGraphicsScene(None)
    compiler = Compiler(Library.load_libraries())

    uml_objects = compiler.compile(code)

    for uml_object in uml_objects.values():
        diagram.add(uml_object)

    # nodes must be updated before layouting
    for node in diagram.nodes.values():
        node.update()

    # needed to layout and draw edges
    diagram.set_anchors()

    Layouter.layout(diagram)

    # edges must be updated after nodes are updated and layouted
    for edge in diagram.edges.values():
        edge.update()

    # this actually paints things, so must be invoked when everything is
    # ready
    for drawable in diagram.elements():
        scene.addItem(drawable)

    sceneRect = QRectF(0,0,0,0)
    
    for node in diagram.nodes.values():
        sceneRect = sceneRect.united(node.globalFullBoundingRect())
        
    esm = 50 # Export scene margins
    sceneRect = sceneRect.adjusted(-esm, -esm, esm, esm)
    scene.setSceneRect(sceneRect)

    img = QImage(scene.sceneRect().toRect().size(), QImage.Format_ARGB32)
    painter = QPainter(img)
    
    absoluteRect = QRectF(0, 0, scene.sceneRect().width(), scene.sceneRect().height())
    painter.fillRect(absoluteRect, QBrush(QColor(255, 255, 255),  Qt.SolidPattern))
    
    painter.resetMatrix()
    scene.render(painter)
    painter.end()
    ret = img.save(output)
    print("Save returned " + str(ret))

    logger = logging.getLogger('compiler')
    if logger.is_empty():
        return 0
    else:
        for e in logger.events:
            print str(e)
        return 1

if __name__ == "__main__":
    exit(main(sys.argv))
