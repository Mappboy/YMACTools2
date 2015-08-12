# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISTools2Dialog
                                 A QGIS plugin
 DPAW Tools for QGIS v 2.x
                             -------------------
        begin                : 2014-08-15
        copyright            : (C) 2014 by GIS Apps, Dept of Parks and Wildlife
        email                : Patrick.Maslen@dpaw.wa.gov.au
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_qgistools2 import Ui_QGISTools2
# create the dialog


class QGISTools2Dialog(QtGui.QDialog, Ui_QGISTools2):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
