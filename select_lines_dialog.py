"""
****************************************************************
 Filter by Selection
                              -------------------
        begin                : 2024-05-31
        copyright            : Shai Sussman
        email                : shai.sussman@gmail.com
****************************************************************
"""
import os
import sys

import qgis
from qgis.PyQt import QtWidgets, uic, QtGui, QtCore, QtWidgets
from qgis.PyQt.QtWidgets import *
from qgis.gui import *
from qgis.utils import *
from qgis.core import QgsProject, QgsVectorLayer, Qgis, QgsWkbTypes, QgsPointXY
from qgis.PyQt.QtCore import pyqtSignal


sys.modules["qgsfieldcombobox"] = qgis.gui
sys.modules["qgsmaplayercombobox"] = qgis.gui

try:
    from qgis.core import QgsMapLayerRegistry
except ImportError:
    pass

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'selectLines.ui'))


class SelectLinesDialog(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        QtWidgets.QDockWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)

        self.setupUi(self)
        self.iface = iface
        self.tool = None
        self.pushButton_draw_lines.clicked.connect(self.draw_lines)



    def closeEvent(self, event):
        self.tool.removeRubberBands()
        self.iface.mapCanvas().unsetMapTool(self.tool)
        self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
        self.closingPlugin.emit()
        event.accept()

    def draw_lines(self):
        self.tool = LineTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.tool)
        self.iface.mapCanvas().setCursor(QtCore.Qt.CrossCursor)

class LineTool(QgsMapTool):
  def __init__(self, canvas):
    self.canvas = canvas
    QgsMapTool.__init__(self, self.canvas)
    self.enable = False
    self.lines = []
    self.rubberBand_list = []
    self.index_max = 5
    for i in range(self.index_max):
      rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
      rubberBand.setColor( QtCore.Qt.red if i == 0 else QtCore.Qt.blue)  
      rubberBand.setWidth(2)
      self.rubberBand_list.append(rubberBand)
    self.index = -1
    self.reset()
    self.startPoints = []
    self.endPoints = []

  def removeRubberBands(self):
    for rubberBand in self.rubberBand_list:
        self.canvas.scene().removeItem(rubberBand)
  def reset(self):
    self.startPoint = self.endPoint = None
    self.isEmittingPoint = False

  def canvasPressEvent(self, e):
    self.startPoint = self.toMapCoordinates(e.pos())
    self.endPoint = self.startPoint
    self.isEmittingPoint = True
    print('press!:', self.index)
    if self.index < self.index_max -1:
      self.index += 1
    else:
      self.index = 0
      print(self.rubberBand_list[-1].asGeometry())

    # self.showLine(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e): 
    # self.panelAction.setIcon(QtGui.QIcon(":/plugins/selectlines/icon2.png"))        self.iface.removeToolBarIcon(self.panelAction)

    self.isEmittingPoint = False
    

  def canvasMoveEvent(self, e):
    if not self.isEmittingPoint:
      return
    self.endPoint = self.toMapCoordinates(e.pos())
    self.showLine(self.startPoint, self.endPoint)

  def showLine(self, startPoint, endPoint):
    if self.index <= self.index_max:
      self.rubberBand_list[self.index].reset(QgsWkbTypes.LineGeometry)
    else:
       return
    if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
      return

    point1 = QgsPointXY(startPoint.x(), startPoint.y())
    point2 = QgsPointXY(endPoint.x(), endPoint.y())

    self.rubberBand_list[self.index].addPoint(point1, False)
    self.rubberBand_list[self.index].addPoint(point2, True) # true to update canvas  
    self.rubberBand_list[self.index].show()
    for i in range(self.index):
      self.rubberBand_list[i].show()

  def deactivate(self):
    # self.canvas.setCursor(QtCore.Qt.ArrowCursor)
    QgsMapTool.deactivate(self)
    self.deactivated.emit()  
   