from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4.QtXml import *
from PyQt4.QtNetwork import QNetworkAccessManager

import xml.etree.ElementTree as ET
import os.path
import platform     # Used to get machine name for counter
import socket       # Used to get IP address for counter
import getpass      # Used to get username for counter
from datetime import datetime
import time
import qgis.utils

import string

#TODO: this whole thing particularly datapaths
#      -Maybe add in photo2shape too ?
class Tools():
    net_manager = QNetworkAccessManager()
    isNewProject = True
    regions = ["Yamatji",
               "Pilbara"]
    errorList = ""
    _region = None
    _dataDrive1 = ""
    _dataDrive2 = ""
    _showDefaultMapDialogue = True
    corpMenuLocation = os.path.abspath(r"\\YMAC-DC3-FS1\Spatial_Data\\")
    menuFileName = "QGIS_tools_menu.xml"
    dataPath = ""
    lastID = 0
    #applicationName = "QGIS Tools"
    applicationName = "YMAC Tools"
    releaseDate = "12/08/2015"
    versionNumber = "2.0"
    QGISApp = None
    dataMenuDict = dict({"null": 0})
    #WMSServerSummaryDict = dict({"null": 0})
    dockableWidgetManager = None
    _pluginPath = ""
    composers = []
    localLogFolder = r"C:\ProgramData\YMAC\GIS"
    localLogFilename = r"\cddp.log"
    localWMSLogFilename = r"\wms.log"
    #TODO: Change this
    centralLogFolder = os.path.abspath(r"\\YMAC-DC3-FS1\General\SpatialLogs\\YMACTools.log")
    machineName = platform.node()
    username = getpass.getuser()
    cddpTechnique = "manual"    # Default for counter method
    lastProject = ""        # Used in cddpTechnique decision
    lastPageSize = "A3"     # Used to decide which radio button is selected on opening the map prod tool (updates so previous one used is checked)
    lastPageOrientation = "Portrait"    # As above but for orientation
    WMSinCDDP = []
    corporateDataDrive = "External"     # Normally this will be overwritten on starting QGIS, with the V: drive address

    iconApp = QIcon(":/plugins/ymactools2/resources/icons/YMAC.png")
    iconFolder = QIcon(":/plugins/ymactools2/resources/icons/folder.png")
    iconGlobe = QIcon(":/plugins/ymactools2/resources/icons/globe.png")
    iconPrinter = QIcon(":/plugins/ymactools2/resources/icons/printer.png")
    iconPageSetup = QIcon(":/plugins/ymactools2/resources/icons/page_white_gear.png")
    iconMapPro = QIcon(":/plugins/ymactools2/resources/icons/map_edit.png")
    iconMapCog = QIcon(":/plugins/ymactools2/resources/icons/map_cog.png")
    iconMapLabel = QIcon(":/plugins/ymactools2/resources/icons/map_edit.png")
    iconZoomLocation = QIcon(":/plugins/ymactools2/resources/icons/binocs.png")
    iconRefresh = QIcon(":/plugins/ymactools2/resources/icons/refresh.png")
    startTime = None
    stopTime = None

#######################
    def __init__(self):
        self.dockableWidgetManager = DataMenu()
        Tools._region = Tools.getRegion()

####################
    @staticmethod
    def getNextID():
        """ Generates a unique string ID. """
        Tools.lastID += 1
        return str(Tools.lastID)

########################
    @staticmethod
    def dataLocation1():
        """ Primary data location. """
        path = Tools.getDataDrive1() + Tools.dataPath
        return Tools.endWithSlash(path)

########################
    @staticmethod
    def dataLocation2():
        """ Secondary data location. """
        path = Tools.getDataDrive2() + Tools.dataPath
        return Tools.endWithSlash(path)

###################################
    @staticmethod
    def findData(relativeLocation, zone=""):
        # Searches the dataDrives for the required file,
        # then returns complete path.

        if relativeLocation.startswith("?"):
            relativeLocation = relativeLocation[1:]
            relativeLocation = Tools.substituteRegion(relativeLocation)
            relativeLocation = Tools.substituteZones(relativeLocation, zone)
            if (os.path.isfile(relativeLocation)):
                return relativeLocation
            else:
                return ""

        # pine plantations imagery tile index has the data path stored in the
        # attribute table.  This will correct:
        if relativeLocation.lower().startswith(Tools.dataPath.lower()):
            relativeLocation = relativeLocation[len(Tools.dataPath):]

        while relativeLocation[0] == "\\":
            relativeLocation = relativeLocation[1:]
        relativeLocation = Tools.substituteRegion(relativeLocation)
        relativeLocation = Tools.substituteZones(relativeLocation, zone)
        path = Tools.dataLocation1() + relativeLocation
        if (os.path.isfile(path)):
            return path
        else:
            path = Tools.dataLocation2() + relativeLocation
            if (os.path.isfile(path)):
                return path
            else:
                return ""

############################
    @staticmethod
    def endWithSlash(input):
        """ Returns the input with trailing slash appended as necessary. """
        if input[-1:] != "\\":
            input += "\\"
        return input

###################################################
    @staticmethod
    def substituteRegion(input, spaceDelimiter="_"):
        """ Replaces %REG% with the current region. """
        region = Tools.getRegion()
        if spaceDelimiter != "_":
            region = region.replace("_", spaceDelimiter)
        return input.replace("%REG%", region)

###################################################
    @staticmethod
    def substituteZones(input, zone=""):
        """ Replaces %REG% with the current region. """
        if zone != "":
            zoneNumber = zone.replace("z", "")
            return input.replace("%ZONE%", zone).replace("%ZONE#%", zoneNumber)
        else:
            return input

###################################
    @staticmethod
    def debug(text, title="Debug"):
        """ Immediately display text for debugging purposes. """
        if text is None:
            text = "None"
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                text2 = "unable to display text\n"
                for x in text:
                    text2 += x
                text = text2
        QMessageBox.information(None, title, text+"\n")

###################################
    @staticmethod
    def alert(text, title="Alert"):
        """ Immediately display text for notification purposes. """
        if not isinstance(text, str):
            text = str(text)
        QMessageBox.information(None, title, text)

###################################
    @staticmethod
    def showYesNoDialog(text, title="Question"):
        """ Ask the user as Yes/No question. """
        if not isinstance(text, str):
            text = str(text)
        messageBox = QMessageBox()
        messageBox.setText(text)
        messageBox.setWindowTitle(title)
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messageBox.setDefaultButton(QMessageBox.Yes)
        return messageBox.exec_() == QMessageBox.Yes

##########################
    @staticmethod
    def logError(message):
        """ Stores an error to be displayed later. """
        if message != "":
            Tools.errorList += message+"\n"

###################################
    @staticmethod
    def flushErrors(title="Error"):
        """ Presents any logged errors to the user. """
        if Tools.errorList != "":
            QMessageBox.information(None, title, Tools.errorList)
            Tools.errorList = ""

##################################
    @staticmethod
    def checkForOTFReprojection():
        """ Check for on the fly reprojection ann CRS conflicts,
            will advise the user if conflict is detected """
        return
        mc = qgis.utils.iface.mapCanvas()
        if not mc.hasCrsTransformEnabled():
            crs = None
            for layer in mc.layers():
                if crs is None:
                    crs = layer.crs()
                elif layer.crs() != crs:
                    #mc.mapRenderer().setProjectionsEnabled(True)
                    mc.mapSettings().setCrsTransformEnabled(True)
                    Tools.alert("""
The current project contains layers of different coordinate reference
systems.  "On the fly projection" has been enabled so that they will display
correctly.

On the fly projection can be enabled/disabled for the current project by
selecting:
Settings - Project Properties... - Coordinate Reference Systems (CRS) - Enable
'on the fly' CRS transformations
OR clicking clicking on the "Globe" icon second right icon of the status bar,
then ticking Enable 'on the fly' CRS transformations

On the fly projection can be enabled/disabled for future projects by
selecting:
Settings - Options... - CRS - Enable 'on the fly' reprojection by default.
                    """)
                    break

################################################
    @staticmethod
    def moveLayersToNewGroup(title, layerCount):
        legend = qgis.utils.iface.legendInterface()
        groupLayer = legend.addGroup(title)
        movedCount = 0
        nextLayer = 0
        while movedCount < layerCount:
            if nextLayer != groupLayer:
                legend.moveLayer(legend.layers()[nextLayer], groupLayer)
                movedCount += 1
            # find group
            layerList = legend.groupLayerRelationship()
            for index, item in enumerate(layerList):
                if item[0] == str(title):
                    groupLayer = index
                    break
            nextLayer += 1
        legend.setGroupExpanded(groupLayer, False)
        return groupLayer

##################################
    @staticmethod
    def getFilenameFromPath(path):
        return os.path.basename(path).split('.', 1)[0]

##################################
    @staticmethod
    def selectTopLegendItem():
        # legend = Tools.iface.mainWindow().findChild(QTreeWidget,
                    # "theMapLegend")   <= QGIS 2.2
        # Quick fix for 2.4 wh should also work in 2.2:
        #legend = Tools.iface.mainWindow().findChildren(QTreeWidget)[0]
        #legend.setCurrentItem(legend.topLevelItem(0))
        # Revamped for 2.8:
        legend = qgis.utils.iface.legendInterface()
        layers = legend.layers()
        if len(layers) > 0:
            legend.setCurrentLayer(layers[0])

##################################
    @staticmethod
    def moveTopLegendItemToBottom():
        #Check but seems only to have been formerly used in map production; QGIS crashes 2.8
        legend = Tools.iface.mainWindow().findChildren(QTreeWidget)[0]
        legend.insertTopLevelItems(legend.topLevelItemCount()-1,
                                   [legend.takeTopLevelItem(0)])

###################################################
    @staticmethod
    def getAttributeFromElement(XMLMenuElement, tag):
        # Gets attributes value from XML element (tag is case insensitive)
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"
        assert isinstance(tag, str), "Bad Parameter"

        value = None
        value = XMLMenuElement.get(tag)
        if value is None:
            for key in XMLMenuElement.keys():
                if key.lower() == tag.lower():
                    value = XMLMenuElement.get(key)
        if value is None:
            value = ""
        return value

##################################
    @staticmethod
    def getModelNodePath(modelNode):
        """ Returns the absolute path of the modelNode. """
        assert isinstance(modelNode, QStandardItem), "Bad Parameter"

        path = modelNode.text()
        parent = modelNode.parent()
        while (parent != 0 and parent is not None):
            path = parent.text() + "\\" + path
            parent = parent.parent()
        return "\\" + path

#####################
    @staticmethod
    def startTimer():
        Tools.startTime = datetime.now()
        Tools.stopTime = None

####################
    @staticmethod
    def stopTimer():
        Tools.stopTime = datetime.now()

####################
    @staticmethod
    def showTimer():
        if Tools.startTime is not None:
            if Tools.stopTime is not None:
                delta = Tools.stopTime - Tools.startTime
                Tools.debug(delta)

######################################
    @staticmethod
    def getSetting(name, default=None):
        settings = QSettings()
        # settings.beginGroup("DEC")
        return str(settings.value("YMAC/" + name, default))
        # settings.endGroup()

################################
    @staticmethod
    def setSetting(name, value):
        settings = QSettings()
        settings.setValue("YMAC/" + name, value)

####################
    @staticmethod
    def getRegion():
        # check member variable
        if Tools._region is not None:
            if Tools._region in Tools.regions:
                return Tools._region
        # check QSettings
        reg = Tools.getSetting("region", Tools.regions[0])
        if reg in Tools.regions:
            Tools._region = reg
            return reg
        # default value
        reg = Tools.regions[0]
        Tools.setRegion(reg)
        return reg


#########################
    @staticmethod
    def setRegion(value):
        assert value in Tools.regions, "Bad Region value"

        Tools._region = value
        Tools.setSetting("region", value)

#############################
    @staticmethod
    def setDataDrive1(value):
        assert Tools.validateDataDrive(value), "Bad datadrive value"

        Tools._dataDrive1 = value
        Tools.setSetting("datadrive1", value)

#############################
    @staticmethod
    def getDataDrive1():
        # check member variable
        if Tools._dataDrive1 is not None:
            if Tools.validateDataDrive(Tools._dataDrive1):
                return Tools._dataDrive1
        # check QSettings
        dd = Tools.getSetting("datadrive1", "V:")
        if Tools.validateDataDrive(dd):
            Tools._dataDrive1 = dd
            return dd
        # default value
        dd = "V:"
        Tools.setDataDrive1(dd)
        return dd


#############################
    @staticmethod
    def setDataDrive2(value):
        assert Tools.validateDataDrive(value), "Bad datadrive value"

        Tools._dataDrive2 = value
        Tools.setSetting("datadrive2", value)


#############################
    @staticmethod
    def getDataDrive2():
        # check member variable
        if Tools._dataDrive2 is not None:
            if Tools.validateDataDrive(Tools._dataDrive2):
                return Tools._dataDrive2
        # check QSettings
        dd = Tools.getSetting("datadrive2", "V:")
        if Tools.validateDataDrive(dd):
            Tools._dataDrive2 = dd
            return dd
        # default value
        dd = "V:"
        Tools.setDataDrive2(dd)
        return dd

#################################
    @staticmethod
    def validateDataDrive(value):
        if not isinstance(value, str):
            Tools.debug("not str")
        if (not isinstance(value, str) or len(value) != 2 or
                value[0] not in string.ascii_letters or value[1] != ":"):
            return False
        else:
            return True

    @staticmethod
    def setPluginPath(path):
        Tools._pluginPath = str(path)

    @staticmethod
    def getPluginPath():
        if len(Tools._pluginPath) > 0:
            return Tools._pluginPath

        # check program files
        pluginPath = (QFileInfo(QgsApplication.pluginPath()).path() +
                      "/python/plugins/ymactools2/")
        pluginFile = QFile(pluginPath)
        if pluginFile.exists():
            Tools._pluginDir = pluginPath
            return pluginPath

        # check user directory
        pluginPath = (QFileInfo(QgsApplication.qgisUserDbFilePath()).path() +
                      "python/plugins/ymactools2/")
        pluginFile = QFile(pluginPath)
        if pluginFile.exists():
            Tools._pluginDir = pluginPath
            return pluginPath

        # report missing plugin
        Tools.debug("We are unable to locate the plugin directory!" +
                    "\nPlease contact GIS Applications for further advice.",
                    "BAD INSTALL")

#############################
    @staticmethod
    def setDockArea(value):
        Tools.setSetting("dockarea", value)


#############################
    @staticmethod
    def getDockArea():
        # check QSettings with default, faster that checking length of
        # returned value, then returning default as needed
        dd = int(Tools.getSetting("dockarea", Qt.LeftDockWidgetArea))

        return dd

    @staticmethod
    def activeLayer():
        if len(qgis.utils.iface.legendInterface().selectedLayers()) == 1:
            return qgis.utils.iface.activeLayer()
        # else:
            # return None

    @staticmethod
    def log(message):
        return
        message = str(message)
        location = "C:/temp/QGISTOOLSLOG.txt"
        try:
            with open(location, "a") as myfile:
                myfile.write(str(datetime.now())+"\t"+message + "\r\n")
        except:
            from time import sleep
            sleep(1)
            Tools.log("log file access Error!\r\n"+message)

    @staticmethod
    def loadWMSPresets():
        settings = QSettings()
        settings.beginGroup("/QGis")

        location = Tools.findData(r"Index\Config\SLIP_WMS_connections.xml")
        xmlFile = QFile(location)
        if not xmlFile.open(QIODevice.ReadOnly | QIODevice.Text):
            return

        domDoc = QDomDocument()
        if not domDoc.setContent(xmlFile, True):
            return

        root = domDoc.documentElement()
        if root.tagName() == "qgsWMSConnections":
            child = root.firstChildElement()
            while not child.isNull():
                connectionName = child.attribute("name")
                settings.setValue("/connections-wms/" + connectionName +
                                  "/url", child.attribute("url"))
                settings.setValue("/connections-wms/" + connectionName +
                                  "/ignoreGetMapURI",
                                  child.attribute("ignoreGetMapURI") == "true")
                settings.setValue("/connections-wms/" + connectionName +
                                  "/ignoreGetFeatureInfoURI",
                                  child.attribute("ignoreGetFeatureInfoURI") == "true")
                # if not child.attribute( "username" ).isEmpty():
                if child.attribute("username") != "":
                    settings.setValue("/WMS/" + connectionName + "/username",
                                      child.attribute("username"))
                    settings.setValue("/WMS/" + connectionName + "/password",
                                      child.attribute("password"))
                child = child.nextSiblingElement()

    @staticmethod
    def loadWFSPresets():
        settings = QSettings()
        settings.beginGroup("/QGis")

        location = Tools.findData(r"Index\Config\SLIP_WFS_connections.xml")
        xmlFile = QFile(location)
        if not xmlFile.open(QIODevice.ReadOnly | QIODevice.Text):
            return

        domDoc = QDomDocument()
        if not domDoc.setContent(xmlFile, True):
            return

        root = domDoc.documentElement()
        if root.tagName() == "qgsWFSConnections":
            child = root.firstChildElement()
            while not child.isNull():
                connectionName = child.attribute("name")
                settings.setValue("/connections-wfs/" + connectionName +
                                  "/url", child.attribute("url"))
                settings.setValue("/connections-wfs/" + connectionName +
                                  "/ignoreGetMapURI",
                                  child.attribute("ignoreGetMapURI") == "true")
                settings.setValue("/connections-wfs/" + connectionName +
                                  "/ignoreGetFeatureInfoURI",
                                  child.attribute("ignoreGetFeatureInfoURI") == "true")
                if child.attribute("username") != "":
                    settings.setValue("/WFS/" + connectionName + "/username",
                                      child.attribute("username"))
                    settings.setValue("/WFS/" + connectionName + "/password",
                                      child.attribute("password"))
                child = child.nextSiblingElement()

    @staticmethod
    def updateCounter(cddpLayer):
        # get path to counter.txt
        folder = os.path.abspath(Tools.localLogFolder)
        counter = os.path.normpath(folder) + Tools.localLogFilename
        project = QgsProject.instance()
        #if project.fileName() != "" and Tools.projectRead == False:    Initial line but did not cater for >1 project per session
        if project.fileName() != Tools.lastProject: # Tools.lastProject is set to project.fileName() once all project layers have been loaded
            Tools.cddpTechnique = "project"
        try:
            user = Tools.username
            machine = Tools.machineName
            #try:
            #    ip = str(socket.gethostbyname(socket.gethostname()))
            #except:
            #    ip = "unknown"
            date = time.strftime("%Y%m%d")
            string = cddpLayer + ", " + user + ", " + machine + ", " + Tools.corporateDataDrive + ", " + date + ", QGIS, " + Tools.cddpTechnique + "\n"
            # open counter.txt in 'append' mode:
            with open(counter, "a") as counterFile:
                counterFile.write(string)
                counterFile.close()
            Tools.cddpTechnique = "manual"
        except IOError:
            # triggered if unable to write to file.
            # NB layer still loads but is not counted
            Tools.debug("counter.txt is open - " +
                        "please close it so that CDDP counts can be made.")
            return

    @staticmethod
    def updateWMSCounter(wmsLayer, url, wmsInCDDP):
        # get path to counter.txt
        folder = os.path.abspath(Tools.localLogFolder)
        wmsCounter = os.path.normpath(folder) + Tools.localWMSLogFilename
        project = QgsProject.instance()
        #if project.fileName() != "" and Tools.projectRead == False:    Initial line but did not cater for >1 project per session
        if project.fileName() != Tools.lastProject: # Tools.lastProject is set to project.fileName() once all project layers have been loaded
            Tools.cddpTechnique = "project"
        try:
            user = Tools.username
            machine = Tools.machineName
            date = time.strftime("%Y%m%d")
            string = wmsLayer + ", " + url + ", " + user + ", " + machine + ", " + Tools.corporateDataDrive + ", " + date + ", QGIS, " + Tools.cddpTechnique + wmsInCDDP + "\n"
            # open counter.txt in 'append' mode:
            with open(wmsCounter, "a") as counterFile:
                counterFile.write(string)
                counterFile.close()
            Tools.cddpTechnique = "manual"
        except IOError:
            # triggered if unable to write to file.
            # NB layer still loads but is not counted
            Tools.debug("wms_counter.txt is open - " +
                        "please close it so that WMS counts can be made.")
            return
