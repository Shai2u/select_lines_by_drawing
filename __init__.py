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
def name():
    return "SelectLines"
def description():
    return " Enables selecting line featuers based that pass through all the drawn lines."
def version():
    return "Version 0.1"
def icon():
    return "icon1.png"
def classFactory(iface):
    # load SelectLines class from file SelectLines
    from .selectlines import SelectLines
    return SelectLines(iface)
