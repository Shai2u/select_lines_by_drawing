"""
****************************************************************
 Filter by Selection
                              -------------------
        begin                : 2024-08-02
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
from qgis.core import *
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
        """
        Initialize the SelectLinesDialog.

        This method sets up the UI, connects the buttons to their respective functions,
        and initializes the necessary variables.

        Parameters:
        - iface (QgisInterface): The QGIS interface object.
        - parent (QWidget): The parent widget.

        Returns:
        None
        """
        # Initialize Plugin widget, UI and setup iface references to QGIS interface object
        QtWidgets.QDockWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.iface = iface
        
        # Initialize the tool attribute to None
        self.tool = None
        
        # Set the automatic mode to True
        self.automatic_mode = True
        
        # Set the name of the annotation layer
        self.annotaiton_layer_name = 'plugin_annotation'
        
        # Connect the tab change event to the on_tab_changed method
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Connect the buttons to the associated emthods
        self.pushButton_draw_lines.clicked.connect(self.draw_lines)
        self.pushButton_reset_lines.clicked.connect(self.reset)
        self.pushButton_select_features.clicked.connect(self.select_features)        
        self.pushButton_init.clicked.connect(self.init_manual)
        self.pushButton_add_lines.clicked.connect(self.add_lines)
        self.pushButton_remove_lines.clicked.connect(self.subtract_lines)
        self.pushButton_filter_lines.clicked.connect(self.filter_lines)       
        
        # Disable the reset lines and select  button initially
        self.pushButton_reset_lines.setEnabled(False)
        self.pushButton_select_features.setEnabled(False)

    def closeEvent(self, event):
        """
        Close event handler for the SelectLinesDialog.
        Unset the tool, and reset the cursor to the default arrow cursor.

        Parameters:
        - event (QCloseEvent): The close event object.

        Returns:
        None
        """
        if self.tool is not None:
          self.tool.removeRubberBands()
        # Find the layer by its name
        layer_check = QgsProject.instance().mapLayersByName(self.annotaiton_layer_name)
        # Check if the layer exists in the Table of Contents
        if len(layer_check) >0:
          QgsProject.instance().removeMapLayer(self.annolayer.id())
        self.iface.mapCanvas().unsetMapTool(self.tool)
        self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
        self.iface.mapCanvas().refresh()
        self.closingPlugin.emit()
        event.accept()

    def on_tab_changed(self, index):
       """
       Handle the tab change event.
 
       Parameters:
       - index (int): The index of the selected tab.
 
       """
       self.reset()
       self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
       print(index)
       if index ==1:
          self.automatic_mode = False
          self.pushButton_add_lines.setEnabled(False)
          self.pushButton_remove_lines.setEnabled(False)
          self.pushButton_filter_lines.setEnabled(False)

       else:
          self.automatic_mode = True




    def draw_lines(self):
      """
      Draws lines on the map canvas using the LineTool.

      This method sets the map tool to LineTool and updates the cursor to a cross cursor.
      It also removes any existing rubber bands if a tool is already active.

      Parameters:
      - None

      Returns:
      - None
      """
      # Reset the state and variables
      self.reset()
      
      # Get the active layer
      self.active_layer = self.iface.activeLayer()
      
      # Remove any existing rubber bands
      if (self.tool is not None):
          self.tool.removeRubberBands()
      
      # Find the layer by its name
      layer_check = QgsProject.instance().mapLayersByName(self.annotaiton_layer_name)
      
      # Check if the layer exists in the Table of Contents
      if len(layer_check) == 0:
          # Create a new annotation layer and add it to the project
          self.annolayer = QgsAnnotationLayer(self.annotaiton_layer_name, QgsAnnotationLayer.LayerOptions(QgsProject.instance().transformContext()))
          QgsProject.instance().addMapLayer(self.annolayer)
          self.annolayer.setFlags(QgsMapLayer.Private)
          self.iface.setActiveLayer(self.active_layer)
      else:
          # Use the existing annotation layer
          self.annolayer = layer_check[0]
      
      # Create a new LineTool instance with the necessary parameters - most imporatnly it is in Automatic mode
      self.tool = LineTool(self.iface.mapCanvas(), self.pushButton_reset_lines, self.pushButton_select_features, self.iface.activeLayer().crs(), self.annolayer, True)
      
      # Set the map tool to LineTool
      self.iface.mapCanvas().setMapTool(self.tool)
      
      # Set the cursor to a cross cursor
      self.iface.mapCanvas().setCursor(QtCore.Qt.CrossCursor)
      
      # Disable the draw lines button after it is clicked
      self.pushButton_draw_lines.setEnabled(False)

    def reset(self):
      """
      Remove the lines from the canvas.

      This method removes the rubber bands (drawn lines) and disables the buttons for resetting lines and selecting features.

      Parameters:
        None

      Returns:
        None
      """
      if self.tool is not None:
          # Remove rubber bands and reset cursor
          self.tool.removeRubberBands()
          self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
          
          # Disable/Enable buttons
          self.pushButton_reset_lines.setEnabled(False)
          self.pushButton_select_features.setEnabled(False)
          self.pushButton_add_lines.setEnabled(False)
          self.pushButton_remove_lines.setEnabled(False)
          self.pushButton_filter_lines.setEnabled(False)
          self.pushButton_draw_lines.setEnabled(True)
          
          # Remove and recreate annotation layer
          if self.annolayer is not None and self.annolayer.isValid():
            QgsProject.instance().removeMapLayer(self.annolayer.id())
            
          self.annolayer = QgsAnnotationLayer(self.annotaiton_layer_name, QgsAnnotationLayer.LayerOptions(QgsProject.instance().transformContext()))
          QgsProject.instance().addMapLayer(self.annolayer)
          self.annolayer.setFlags(QgsMapLayer.Private)
          
          # Set active layer
          self.iface.setActiveLayer(self.active_layer)

    def select_features(self):
      """
      Selects features in the active layer based on drawn lines.
      Returns:
        None
      Raises:
        None
      """
      # Set cursor to regular arrow
      self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)

      # Check if active layer is valid and if tool is initialized
      layer = self.iface.activeLayer()
      if not layer or not layer.isValid():
        self.iface.messageBar().pushMessage("Error", "Invalid layer provided.", level=Qgis.Critical)
        return
      if self.tool is None:
        self.iface.messageBar().pushMessage("Error", "No Drawn lines", level=Qgis.Critical)
        return
      
      # get a set of the currently selected features
      set_of_ids_to_select = set(feature.id() for feature in layer.selectedFeatures())

      # prepare transform - this is needed to draw the lines in the layer coordinates system
      project_crs = QgsProject.instance().crs()
      layer_crs = layer.crs()
      transform = QgsCoordinateTransform(project_crs, layer_crs, QgsProject.instance().transformContext())

      # Iterate over the drawn lines and get the IDs of the lines that intersect with them
      for i, rubber_band_dict in enumerate(self.tool.rubberBand_list):
        drawn_geometry = rubber_band_dict['geom'].asGeometry()
        # Transform the geometry to the layer's CRS
        drawn_geometry.transform(transform)
        if not drawn_geometry.isNull():
          lines_intersect_ids = self.get_line_ids(layer, drawn_geometry)
          if rubber_band_dict['operation'] == 'add':
            set_of_ids_to_select = set_of_ids_to_select.union(lines_intersect_ids)
          elif rubber_band_dict['operation'] == 'filter':
            set_of_ids_to_select = set_of_ids_to_select.intersection(lines_intersect_ids)
          else:
            set_of_ids_to_select = set_of_ids_to_select.difference(lines_intersect_ids)

        layer.selectByIds(list(set_of_ids_to_select))
      
      # Refresh the layer to update the selection
      self.tool.index = self.tool.index_max
      layer.triggerRepaint()

      # Provide feedback
      self.iface.messageBar().pushMessage("Info", f"Selected {layer.selectedFeatureCount()} features.", level=Qgis.Info)
      
      # Enable Disable buttons
      self.pushButton_select_features.setEnabled(False)
      self.pushButton_add_lines.setEnabled(False)
      self.pushButton_remove_lines.setEnabled(False)
      self.pushButton_filter_lines.setEnabled(False)
      self.pushButton_draw_lines.setEnabled(True)
        


    def init_manual(self):
      """
      Initialize the manual mode for selecting lines.

      This method sets the cursor to the default arrow cursor and enables the buttons for adding, removing, and filtering lines.
      It also creates or retrieves the annotation layer and sets the map tool to LineTool in manual mode.

      Parameters:
      - None

      Returns:
      - None
      """
      # Set the cursor to the default arrow cursor
      self.iface.mapCanvas().setCursor(QtCore.Qt.ArrowCursor)
      
      # Enable the buttons for adding, removing, and filtering lines
      self.pushButton_add_lines.setEnabled(True)
      self.pushButton_remove_lines.setEnabled(True)
      self.pushButton_filter_lines.setEnabled(True)
      
      # Get the active layer
      self.active_layer = self.iface.activeLayer()
      
      # Check if active layer is valid and if tool is initialized
      if not self.active_layer or not self.active_layer.isValid():
        self.iface.messageBar().pushMessage("Error", "Invalid layer provided.", level=Qgis.Critical)
        return
      
      if self.tool is not None:
        # Remove any existing rubber bands
        self.tool.removeRubberBands()

      # Find the layer by its name
      layer_check = QgsProject.instance().mapLayersByName(self.annotaiton_layer_name)
      
      # Check if the layer exists in the Table of Contents
      if len(layer_check) == 0:

        # Create a new annotation layer and add it to the project
        self.annolayer = QgsAnnotationLayer(self.annotaiton_layer_name, QgsAnnotationLayer.LayerOptions(QgsProject.instance().transformContext()))
        QgsProject.instance().addMapLayer(self.annolayer)
        
        # Make the annotaiton layer private that means invislbe in TOC
        self.annolayer.setFlags(QgsMapLayer.Private)
        self.iface.setActiveLayer(self.active_layer)
      else:
        # Use the existing annotation layer
        self.annolayer = layer_check[0]
      
      # Create a new LineTool instance with the necessary parameters - most importantly it is in Manual mode
      self.tool = LineTool(self.iface.mapCanvas(), self.pushButton_reset_lines, self.pushButton_select_features, self.iface.activeLayer().crs(), self.annolayer, False)
    
    def add_lines(self):
      """
      Set the map tool to LineTool in add mode.

      This method sets the operation attribute of the LineTool to 'add' and updates the cursor to a cross cursor.

      Parameters:
      - None

      Returns:
      - None
      """
      self.tool.operation = 'add'
      self.iface.mapCanvas().setMapTool(self.tool)
      self.iface.mapCanvas().setCursor(QtCore.Qt.CrossCursor)

    def subtract_lines(self):
      """
      Set the map tool to LineTool in remove mode.

      This method sets the operation attribute of the LineTool to 'remove' and updates the cursor to a cross cursor.

      Parameters:
      - None

      Returns:
      - None
      """
      self.tool.operation = 'remove'
      self.iface.mapCanvas().setMapTool(self.tool)
      self.iface.mapCanvas().setCursor(QtCore.Qt.CrossCursor)  

    def filter_lines(self):
      """
      Set the map tool to LineTool in filter mode.

      This method sets the operation attribute of the LineTool to 'filter' and updates the cursor to a cross cursor.

      Parameters:
      - None

      Returns:
      - None
      """
      self.tool.operation = 'filter'
      self.iface.mapCanvas().setMapTool(self.tool)
      self.iface.mapCanvas().setCursor(QtCore.Qt.CrossCursor) 

    def get_line_ids(self, layer, drawn_geometry):
      """
      Get the IDs of lines in a layer that intersect with a given geometry.
      Parameters:
      - layer (QgsVectorLayer): The layer containing the lines.
      - drawn_geometry (QgsGeometry): The geometry to check for intersection.
      Returns:
      - intersecting_ids (set): A set of IDs of lines that intersect with the given geometry.
      """
      intersecting_ids = set()
      for feature in layer.getFeatures():
          feature_geom = feature.geometry()
          # Check if the feature's geometry intersects with the query geometry
          if feature_geom.intersects(drawn_geometry):
              intersecting_ids.add(feature.id())
  
      return intersecting_ids
    
class LineTool(QgsMapTool):
  def __init__(self, canvas, reset_button, select_features_button, layer_crs, annolayer, automatic = True):
    self.canvas = canvas
    QgsMapTool.__init__(self, self.canvas)
    self.enable = False
    self.automatic_mode = automatic
    # if automatic_mode is False, than we will use the self.operation attribute to determine the operation to be performed
    self.operation = 'none'
    self.layer_crs = layer_crs
    self.annolayer = annolayer 
    self.lines = []
    self.rubberBand_list = []
    self.index_max = 25
    self.reset_button = reset_button
    self.select_features_button = select_features_button
    self.rb_config = {'add': {'color': QtCore.Qt.green, 'width': 4, 'secondary_color': QtCore.Qt.red, 'line_style': QtCore.Qt.SolidLine},
                                   'filter': {'color': QtCore.Qt.blue, 'width': 4, 'secondary_color': QtCore.Qt.red, 'line_style': QtCore.Qt.SolidLine},
                                   'remove': {'color': QtCore.Qt.black, 'width': 4, 'secondary_color': QtCore.Qt.red, 'line_style': QtCore.Qt.SolidLine}}
    for i in range(self.index_max):
      rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
      if i==0:
         rubber_band_dict = {'operation':'add',
                      'geom': rubberBand}
      else:
         rubber_band_dict = {'operation':'filter',
                      'geom': rubberBand}       
      self.rubberBand_list.append(rubber_band_dict)
    self.index = -1
    self.reset()
    self.startPoints = []
    self.endPoints = []

  def removeRubberBands(self):
    """
    Remove all rubber bands from the canvas.

    This method removes all rubber bands (drawn lines) from the canvas scene.

    Parameters:
      None

    Returns:
      None
    """
    for rubberBand in self.rubberBand_list:
        self.canvas.scene().removeItem(rubberBand['geom'])


  def reset(self):
    """
    Reset the start and end points of the line selection.

    This method sets the `startPoint` and `endPoint` attributes to `None` and
    the `isEmittingPoint` attribute to `False`.
    """
    self.startPoint = self.endPoint = None
    self.isEmittingPoint = False

  def canvasPressEvent(self, e):
    """
    Handle the canvas press event, sets the reset and select features buttons to enabled if the index is less than the maximum index.

    Parameters:
      e (QMouseEvent): The mouse event object.

    Returns:
      None
    """
    self.startPoint = self.toMapCoordinates(e.pos())
    self.endPoint = self.startPoint
    self.isEmittingPoint = True
    if self.index < self.index_max -1:
      self.index += 1
      self.reset_button.setEnabled(True)
      self.select_features_button.setEnabled(True)
    else:
      self.index = 0

  def canvasReleaseEvent(self, e): 
    """
    Handle the release event of the canvas.

    Parameters:
    e (QMouseEvent): The event object representing the release event.

    Returns:
    None
    """
    self.isEmittingPoint = False
    self.add_index_anottation(self.index, self.rubberBand_list[self.index]['geom'].asGeometry())

    

  def canvasMoveEvent(self, e):
    """
    Handle the canvas move event.

    Parameters:
    - e (QMouseEvent): The mouse event object.

    Returns:
    - None

    Description:
    This method is called when the cursor is moved int the canvas. It updates the end point of the line being drawn and shows the line on the canvas.

    """
    if not self.isEmittingPoint:
      return
    self.endPoint = self.toMapCoordinates(e.pos())
    self.showLine(self.startPoint, self.endPoint)

  def _configure_rubberband(self, rubberBand, operation):
    rubberBand['operation'] = operation
    rubberBand['geom'].setColor(self.rb_config[operation]['color'])  
    rubberBand['geom'].setWidth(self.rb_config[operation]['width'])
    rubberBand['geom'].setSecondaryStrokeColor(self.rb_config[operation]['secondary_color'])
    rubberBand['geom'].setLineStyle(self.rb_config[operation]['line_style'])
    return rubberBand


  def showLine(self, startPoint, endPoint):
    """
    Show the lines on the canvas between that were drawn by the rubber bands given start and end point.

    Parameters:
    - startPoint (QPointF): The starting point of the line.
    - endPoint (QPointF): The ending point of the line.

    Returns:
    None
    """
    if self.index <= self.index_max:
      self.rubberBand_list[self.index]['geom'].reset(QgsWkbTypes.LineGeometry)
    else:
       return
    if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
      return

    point1 = QgsPointXY(startPoint.x(), startPoint.y())
    point2 = QgsPointXY(endPoint.x(), endPoint.y())
    if self.automatic_mode:
      if self.index == 0:
        self.rubberBand_list[self.index] = self._configure_rubberband(self.rubberBand_list[self.index], 'add')
      else:
        self.rubberBand_list[self.index] = self._configure_rubberband(self.rubberBand_list[self.index], 'filter')
    else:
      self.rubberBand_list[self.index] = self._configure_rubberband(self.rubberBand_list[self.index], self.operation)  
  
    self.rubberBand_list[self.index]['geom'].addPoint(point1, False)
    self.rubberBand_list[self.index]['geom'].addPoint(point2, True) # true to update canvas  
    self.rubberBand_list[self.index]['geom'].show()

    
  def add_index_anottation(self, index, geom):
      """
      Add an annotation from a given X,Y coordinate.

      Parameters:
      - index (int): The index of the annotation.
      - geom (QgsGeometry): The geometry representing the X,Y coordinate.

      Returns:
      None

      Raises:
      None

      Notes:
      - This method adds an annotation to the map canvas at the specified X,Y coordinate.
      - The annotation is represented by a text item with the index number.
      - The text item is styled with a buffer of size 2 and white color.
      """

      # Perform test to see if points are in range if so return a geometry to center upon and continue testing
      if  geom.wkbType().name != 'Unknown':
        x = geom.asPolyline()[0].x() - 200
        y = geom.asPolyline()[0].y()

        a = QgsAnnotationPointTextItem(f"{index + 1}", QgsPointXY(x, y))

        # # 4. Create a QgsTextFormat object to handle the buffer
        text_format = QgsTextFormat()

        # # Set up the buffer settings
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(2)  # Size of the buffer
        buffer_settings.setColor(QtCore.Qt.white)  # Color of the buffer
        text_format.setBuffer(buffer_settings)
        a.setFormat(text_format)
        self.annolayer.addItem(a)


  def deactivate(self):
    """
    Deactivates the QgsMapTool and emits the 'deactivated' signal.
    """
    QgsMapTool.deactivate(self)
    self.deactivated.emit()  
