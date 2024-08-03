# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SelectLines
                                 A QGIS plugin
 SelectLines
                             -------------------
        begin                : 2024-08-02
        copyright            : (C) 2024 by Shai Sussman
        email                : SelectLines
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
# Import the PyQt and QGIS libraries
from PyQt5 import Qt, QtCore, QtWidgets, QtGui
import subprocess
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .resources_rc import *
# Import the code for the dialog
import os.path
rl=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.LineGeometry )
premuto= False
linea=False
point0=iface.mapCanvas().getCoordinateTransform().toMapCoordinates(0, 0)
point1=iface.mapCanvas().getCoordinateTransform().toMapCoordinates(0, 0)
class SelectLines:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        



    def initGui(self):
        self.action = QtWidgets.QAction(QtGui.QIcon(":/plugins/selectlines/icon.png"),u"SelectLines", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&SelectLines", self.action)
        
    def unload(self):
        self.iface.removePluginMenu(u"&SelectLines", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self): 


        tool = LineTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(tool)     


class LineTool(QgsMapTool):
  def __init__(self, canvas):
    self.canvas = canvas
    QgsMapTool.__init__(self, self.canvas)
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
    self.isEmittingPoint = False
    

  def canvasMoveEvent(self, e):
    self.canvas.setCursor(QtCore.Qt.CrossCursor)
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
    QgsMapTool.deactivate(self)
    self.deactivated.emit()  
   