from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
import xml.etree.ElementTree as ET
from ...tools import Tools


class LoadShapefile():

    #####################
    def __init__(self):
        self.title = ""
        self.directory = ""
        self.shapefile = ""
        self.layerfile = ""
        self.caveat = ""


####################
    def isValid(self):
        """ Validates the LoadShapefile. """
        if (self.title is None or self.shapefile is None or self.directory is None):
            return False
        if (len(self.title) > 0 and len(self.shapefile) > 0 and len(self.directory) > 0):
            return True
        else:
            return False


#####################
    def doLoad(self):
        # Loads shapefile and attaches resultant layer to QgsMapLayerRegistry.
        directory = Tools.endWithSlash(self.directory)
        shpLocation = directory + self.shapefile
        title = Tools.substituteRegion(self.title, " ")
        layer = LoadShapefile.loadShapefile(shpLocation, title)
        if (layer is not None):
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            if self.caveat != "" and self.caveat is not None:
                Tools.alert(self.caveat, "Caveat")
            return True
        else:
            return False


#########################################
    @staticmethod
    def loadShapefile(filePath, title=""):
        """ Loads a shapefile from disk and returns a QgsVectorLayer containing it. """
        assert isinstance(filePath, str), "Bad Parameter"
        assert isinstance(title, str), "Bad Parameter"

        if title == "":
            title = Tools.getFilenameFromPath(filePath)

        shpLocation = Tools.findData(filePath)
        if (shpLocation != ""):
            title = Tools.substituteRegion(title, " ")
            layer = QgsVectorLayer(shpLocation, title, "ogr")
            if layer.isValid():
                return layer
            else:
                Tools.logError("Invalid data found at " + shpLocation)
                return None
        else:
            Tools.logError("Unable to locate " + title)
            return None

##############################################
    @staticmethod
    def parseXML(XMLMenuElement):
        """ Create a LoadShapefile from data in the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"

        loadShapefile = LoadShapefile()
        loadShapefile.title = Tools.getAttributeFromElement(XMLMenuElement, "title")
        loadShapefile.directory = Tools.getAttributeFromElement(XMLMenuElement, "directory")
        loadShapefile.shapefile = Tools.getAttributeFromElement(XMLMenuElement, "shapefile")
        loadShapefile.layerfile = Tools.getAttributeFromElement(XMLMenuElement, "layerfile")
        loadShapefile.caveat = Tools.getAttributeFromElement(XMLMenuElement, "caveat")
        if loadShapefile.isValid():
            return loadShapefile
        else:
            return None
