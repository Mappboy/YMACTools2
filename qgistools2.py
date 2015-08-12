# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISTools2
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from qgistools2dialog import QGISTools2Dialog
from os import makedirs, path
import time
import win32com.client  # Used to obtain V: drive address on starting QGIS (see QGISTools2.__init__)
import shutil           # Used to copy project_default.qgs from resources folder to new user's .qgis2 folder
from dec.gis.qgis.ui.dockablewindow import DockableWindow
from dec.gis.qgis.tools import Tools
from dec.gis.qgis.mapproduction.mapproduction import MapProduction
from dec.gis.qgis.ui.showProjectTemplateDialog import ShowProjectTemplateDialog

# import sys
# sys.path.append("C:\\Users\\patrickm\\Desktop\\GISTools\\eclipseNEW\\plugins\\org.python.pydev_3.8.0.201409251235\\pysrc\\")
# from pydevd import*


class QGISTools2:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        Tools.iface = iface
        self.templateDialog = None
        # initialize plugin directory
        self.plugin_dir = path.normpath(path.join(path.dirname(__file__), ("..")))
        #Tools.debug(self.plugin_dir)
        #Tools.debug(str(QgsApplication.pluginPath()).replace("\\", "/").rsplit("/", 1)[0] + "/python/plugins/qgistools")
        if not QFileInfo(self.plugin_dir).exists():
            self.plugin_dir = str(QgsApplication.pluginPath()).replace("\\", "/").rsplit("/", 1)[0] + "/python/plugins/qgistools"

        # Check whether this user has a .qgis2 folder containing project_default.qgs
        userProjDefaultLocation = "C:/Users/" + Tools.username + "/.qgis2/project_default.qgs"
        #TODO: Change this to YMAC default project
        pluginProjDefaultLocation = path.dirname(__file__) + "/resources/project_default_DPaW.qgs"
        if not path.exists(userProjDefaultLocation):
            shutil.copyfile(pluginProjDefaultLocation, userProjDefaultLocation)

        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = path.join(self.plugin_dir, 'i18n', 'qgistools2_{}.qm'.format(locale))

        if path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = QGISTools2Dialog() #commented out PWM

        # Upload local WMS counter data to central counter
        # Check if local WMS log file exists; if not then create it.
        try:
            makedirs(Tools.localLogFolder)
        except:
            pass
        localWmsFilename = path.normpath(Tools.localLogFolder) + Tools.localWMSLogFilename
        if not path.exists(localWmsFilename):
            fromFile = open(localWmsFilename, "w+")    # Creates local log file if it does not exist"
        else:
            fromFile = open(localWmsFilename, "r+")    # Allows us to overwrite (to empty string)
        text = fromFile.read()

        if text != "":
            # check for central log file for this month
            try:
                centralWMSFilename = str(Tools.centralLogFolder) + "\wms_" + time.strftime("%Y%m") + ".log"
                if not path.exists(centralWMSFilename):
                    toFile = open(centralWMSFilename, "w+")
                else:
                    toFile = open(centralWMSFilename, "a")
                toFile.write(text)
                toFile.close()
                fromFile.seek(0, 0)     # Return cursor to start of file
                fromFile.truncate()     # Remove contents
            except:
                pass
            fromFile.close()


        # Upload local CDDP counter data to central counter
        # Check if local log file exists; if not then create it.
        localFilename = path.normpath(Tools.localLogFolder) + Tools.localLogFilename
        if not path.exists(localFilename):
            fromFile = open(localFilename, "w+")    # Creates file if it does not exist"
        else:
            fromFile = open(localFilename, "r+")    # Allows us to overwrite (to empty string)
        text = fromFile.read()
        if text != "":
            # check for central log file for this month
            try:
                centralFilename = str(Tools.centralLogFolder) + "\cddp_" + time.strftime("%Y%m") + ".log"
                if not path.exists(centralFilename):
                    toFile = open(centralFilename, "w+")
                else:
                    toFile = open(centralFilename, "a")
                toFile.write(text)
                toFile.close()
                fromFile.seek(0, 0)     # Return cursor to start of file
                fromFile.truncate()     # Remove contents
            except:
                pass
            fromFile.close()

        # Get V: drive address if it exists - see http://www.thescriptlibrary.com/Default.asp?Action=Display&Level=Category3&ScriptLanguage=Python&Category1=Storage&Category2=Disk%20Drives%20and%20Volumes&Title=List%20Mapped%20Network%20Drives
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        mappedDrives = objSWbemServices.ExecQuery("Select * from Win32_MappedLogicalDisk")
        for drive in mappedDrives:
            if drive.Name == "V:":
                Tools.corporateDataDrive = drive.ProviderName
    #TODO:
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/qgistools2/DPAW.png"),
            u"YMAC Tools for QGIS v 2.x", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&QGIS Tools 2", self.action)

        self.iface.newProjectCreated.connect(self.newProject)
        self.iface.projectRead.connect(self.loadProject)
        QgsMapLayerRegistry.instance().layersAdded.connect(self.layersAdded)

        Tools.loadWMSPresets()
        Tools.loadWFSPresets()
        DockableWindow.getDockable(True)


    def unload(self):
        # Remove the plugin menu item, icon and interface
        self.iface.removePluginMenu(u"&QGIS Tools 2", self.action)
        self.iface.removeToolBarIcon(self.action)
        mw = self.iface.mainWindow()
        dock = mw.findChild(QDockWidget, Tools.applicationName)
        mw.removeDockWidget(dock)


    def run(self):
        DockableWindow.getDockable()


    def newProject(self):
        Tools.isNewProject = True
        Tools.projectRead = False
        sb = Tools.iface.mainWindow().statusBar()
        sb.messageChanged.connect(self.showProjectTemplateDialog)


    def showProjectTemplateDialog(self):
            setting = Tools.getSetting("showDefaultMapDialog")
            if setting != "false":
                sb = Tools.iface.mainWindow().statusBar()
                if sb.currentMessage() == "Project loaded":
                    sb.messageChanged.disconnect()
                    templateDialog = ShowProjectTemplateDialog()
                    #self.previousStatusMessage = "Project loaded"
                #elif sb.currentMessage() == "":
                #    if self.previousStatusMessage == "Project loaded":
                        #dialogue = ShowProjectTemplateDialog()
                        #self.previousStatusMessage == ""
                else:
                    pass
                    #self.previousStatusMessage == ""


    def loadProject(self):
        Tools.isNewProject = False
        project = QgsProject.instance()
        Tools.lastProject = project.fileName()

    def layersAdded(self, layers):
        layer = layers[-1]
        if Tools.isNewProject:
            crs = layer.crs()
            settings = self.iface.mapCanvas().mapSettings()
            settings.setDestinationCrs(crs)
            settings.setCrsTransformEnabled(True)
            Tools.isNewProject = False

        source = layer.source().replace("\\", "/")
        dataLocation = Tools.dataLocation1().replace("\\", "/")
        if source.startswith(dataLocation):     # i.e. if starts with "V:/GIS1-Corporate/Data/"
            start = len(dataLocation)
            cddpLayer = source[start:]
            Tools.updateCounter(cddpLayer)
        if layer.type() == QgsMapLayer.RasterLayer and layer.dataProvider().name() == "wms":
            url = ""
            layers = ""
            src = layer.source()
            srcParams = src.split("&")
            for param in srcParams:
                if param[:4] == "url=":
                    url = param[4:]
                elif param[:7] == "layers=":
                    layers = param[7:]
            wmsParams = (url, layers)
            wmsInCDDP = "start value"
            if Tools.cddpTechnique == "menu":
                wmsInCDDP = ""
            else:
                if wmsParams in Tools.WMSinCDDP:
                    wmsInCDDP = " - CDDP layer"
                else:
                    wmsInCDDP = " - Non-CDDP layer"
            Tools.updateWMSCounter(layer.name(), url, wmsInCDDP)

