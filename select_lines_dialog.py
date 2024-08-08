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
from qgis.core import QgsProject, QgsVectorLayer, Qgis, QgsWkbTypes, QgsPointXY, QgsCoordinateTransform
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
        self.pushButton_reset_lines.clicked.connect(self.remove_lines)
        self.pushButton_select_features.clicked.connect(self.select_features)
        self.pushButton_reset_lines.setEnabled(False)
        self.pushButton_select_features.setEnabled(False)        



    def closeEvent(self, event):
        if self.tool is not None:
          self.tool.removeRubberBands()
        self.iface.mapCanvas().unsetMapTool(self.tool)
        self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
        self.closingPlugin.emit()
        event.accept()

    def draw_lines(self):
        if (self.tool is not None):
            self.tool.removeRubberBands()
        self.tool = LineTool(self.iface.mapCanvas(),  self.pushButton_reset_lines,  self.pushButton_select_features)
        self.iface.mapCanvas().setMapTool(self.tool)
        self.iface.mapCanvas().setCursor(QtCore.Qt.CrossCursor)

    def remove_lines(self):
      if self.tool is not None:
          self.tool.removeRubberBands()
          self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
          self.pushButton_reset_lines.setEnabled(False)
          self.pushButton_select_features.setEnabled(False)
      
    def select_features(self):
      layer = self.iface.activeLayer()
      if not layer or not layer.isValid():
        self.iface.messageBar().pushMessage("Error", "Invalid layer provided.", level=Qgis.Critical)
        return
      if self.tool is None:
        self.iface.messageBar().pushMessage("Error", "No Drawn lines", level=Qgis.Critical)
        return
      self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
      
      # Deselect all features first
      layer.removeSelection()
      # Create a set to hold IDs of intersecting features
      intersecting_ids = set()

      # First selection
      drawn_geometry = self.tool.rubberBand_list[0].asGeometry()

      project_crs = QgsProject.instance().crs()
      layer_crs = layer.crs()
      if project_crs!=layer_crs:
        # Create coordinate transform object
        transform = QgsCoordinateTransform(project_crs, layer_crs, QgsProject.instance().transformContext())
        # Transform the geometry to the layer's CRS
        drawn_geometry.transform(transform)

      transform = QgsCoordinateTransform(project_crs, layer_crs, QgsProject.instance().transformContext())
      for feature in layer.getFeatures():
        feature_geom = feature.geometry()
        # Check if the feature's geometry intersects with the query geometry
        if feature_geom.intersects(drawn_geometry):
            intersecting_ids.add(feature.id())
      # Select the features by IDs
      layer.selectByIds(list(intersecting_ids))
      # Refresh the layer to update the selection
      layer.triggerRepaint()
      # filter from first selection
      for i in range(1, len(self.tool.rubberBand_list)):
        drawn_geometry = self.tool.rubberBand_list[i].asGeometry()
        # Transform the geometry to the layer's CRS
        drawn_geometry.transform(transform)
        if not drawn_geometry.isNull():
          sub_intersecting_ids = set()
          currently_selected_ids = layer.selectedFeatureIds()
          for selected_id in currently_selected_ids:
            feature_geom = layer.getFeature(selected_id).geometry()
            if feature_geom.intersects(drawn_geometry):
              sub_intersecting_ids.add(selected_id)
          layer.selectByIds(list(sub_intersecting_ids))
          # Refresh the layer to update the selection
      layer.triggerRepaint()
           


      # Provide feedback
      self.iface.messageBar().pushMessage("Info", f"Selected {len(intersecting_ids)} features.", level=Qgis.Info)
      self.pushButton_select_features.setEnabled(False)


class LineTool(QgsMapTool):
  def __init__(self, canvas, reset_button, select_features_button):
    self.canvas = canvas
    QgsMapTool.__init__(self, self.canvas)
    self.enable = False
    self.lines = []
    self.rubberBand_list = []
    self.index_max = 5
    self.reset_button = reset_button
    self.select_features_button = select_features_button
    for i in range(self.index_max):
      rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
      rubberBand.setColor( QtCore.Qt.red if i == 0 else QtCore.Qt.blue)  
      rubberBand.setWidth(4)
      rubberBand.setSecondaryStrokeColor(QtCore.Qt.green)
      rubberBand.setLineStyle(QtCore.Qt.SolidLine)
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
    if self.index < self.index_max -1:
      self.index += 1
      self.reset_button.setEnabled(True)
      self.select_features_button.setEnabled(True)
    else:
      self.index = 0

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
   