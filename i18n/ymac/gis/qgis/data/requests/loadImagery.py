from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import xml.etree.ElementTree as ET
from ...tools import Tools


class LoadImagery():

    #####################
    def __init__(self):
        self.title = ""
        self.imagefile = ""


####################
    def isValid(self):
        """ Validates the LoadImagery. """
        if self.title is None or self.imagefile is None:
            return False

        if len(self.title) > 0 and len(self.imagefile) > 0:
            return True
        else:
            return False

#####################
    def doLoad(self, directory="", zone=""):
        # Loads imagery and attaches resultant layer to QgsMapLayerRegistry.
        if directory != "":
            directory = Tools.endWithSlash(directory)
        imageLocation = directory + self.imagefile
        title = Tools.substituteRegion(self.title, " ")
        title = Tools.substituteZones(title, zone)
        layer = LoadImagery.loadImagery(imageLocation, title, zone)
        imageryLocation = Tools.findData(directory + self.imagefile, zone)
        if (layer is not None):
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            return True
        else:
            return False

###############################################
    @staticmethod
    def loadImagery(filePath, title="", zone=""):
        # Loads imagery from disk and returns a QgsRasterLayer containing it.
        assert isinstance(filePath, str), "Bad Parameter"
        assert isinstance(title, str), "Bad Parameter"

        if title == "":
            title = Tools.getFilenameFromPath(filePath)
        # Special case for one entry (Myalup in Pine Plantation Map Imagery) - missing ".map" at end of entry in index attribute table
        if "\\data\\imagery\\plantations\\" in filePath.lower() and filePath[-1:] == ".":
            filePath = filePath[:-1] + ".map"
        imageLocation = Tools.findData(filePath, zone)
        if (imageLocation != ""):
            # Pine Plantation Map imagery .tif files do not load correctly; .map files do
            if "\\Data\\Imagery\\Plantations\\" in imageLocation and imageLocation[-4:] == ".tif":
                imageLocation = imageLocation[:-4] + ".map"
            title = Tools.substituteRegion(title, " ")
            layer = QgsRasterLayer(imageLocation, title)
            if layer.isValid():
                return layer
            else:
                Tools.logError("Invalid data found at " + imageLocation)
                return None
        else:
            Tools.logError("Unable to locate " + title)
            return None

##############################################
    @staticmethod
    def parseXML(XMLMenuElement):
        """ Create a LoadImagery from data in the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"

        loadImagery = LoadImagery()
        loadImagery.title = Tools.getAttributeFromElement(XMLMenuElement,
                                                          "title")
        loadImagery.imagefile = Tools.getAttributeFromElement(XMLMenuElement,
                                                              "imagefile")
        if loadImagery.isValid():
            return loadImagery
        else:
            return None
