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
from .select_lines_dialog import SelectLinesDialog

# Import the code for the dialog
import os.path
class SelectLines:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.pluginIsActive = False
        self.dockwidget = None

    def initGui(self):
        self.panelAction = QtWidgets.QAction(QtGui.QIcon(":/plugins/selectlines/icon.png"),u"SelectLines", self.iface.mainWindow())
        self.panelAction.triggered.connect(self.run)
        self.panelAction.setCheckable(True)
        self.panelAction.setEnabled(True)

        self.iface.addToolBarIcon(self.panelAction)
        self.iface.addPluginToMenu(u"&SelectLines", self.panelAction)
        
    def unload(self):
        self.iface.removePluginMenu(u"&SelectLines", self.panelAction)
        self.iface.removeToolBarIcon(self.panelAction)
   
    def widgetVisibilityChanged(self, visible: bool) -> None:
        self.panelAction.setChecked(visible)
    
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False

    def run(self, checked: bool): 
      """
      Run method for the SelectLines plugin.

      Parameters:
      - checked (bool): Indicates whether the plugin is ready to be displayed

      Returns:
      - None
      """
      if not self.pluginIsActive:
        if self.dockwidget is None:
            self.dockwidget = SelectLinesDialog(self.iface)
        self.dockwidget.visibilityChanged.connect(self.widgetVisibilityChanged)
        self.dockwidget.closingPlugin.connect(self.onClosePlugin)

        self.iface.addDockWidget(
            area=QtCore.Qt.LeftDockWidgetArea,
            dockwidget=self.dockwidget,
        )
      self.dockwidget.setVisible(checked)  

