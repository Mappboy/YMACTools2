from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils

import xml.etree.ElementTree as ET

from ...tools import Tools
from .loadImagery import LoadImagery


class LayerGroup():

    #####################
    def __init__(self):
        self.title = ""
        self.directory = ""
        self.zones = ""
        self.loadImagerys = list()


####################
    def isValid(self):
        """ Validates the LayerGroup. """
        if self.title is None:
            return False

        if len(self.title) == 0 or len(self.loadImagerys) == 0:
            return False
        else:
            return True


#####################
    def doLoad(self):
        """ Iterates through each all data request lists. """

        self.layerCount = 0
        self.doLoadImagerys()

        if self.layerCount > 0:
            Tools.moveLayersToNewGroup(self.title, self.layerCount)
        else:
            Tools.logError("Unable to load any layers for LayerGroup " +
                           self.title)
        return True


#########################################
    def addLoadImagery(self, loadImagery):
        """ Appends the loadImagery to required list """
        assert isinstance(loadImagery, LoadImagery), "Bad Parameter"

        if loadImagery is not None:
            self.loadImagerys.append(loadImagery)


#############################
    def doLoadImagerys(self):
        """ Iterates through loadImagerys actioning each in turn """
        if self.zones == "" or self.zones is None:
            for request in self.loadImagerys:
                self.layerCount += request.doLoad(self.directory)
                # if request.doLoad(self.directory)==1:
                #   self.layerCount += 1

        else:
            zones = self.zones.split(";")
            for request in self.loadImagerys:
                for zone in zones:
                    self.layerCount += request.doLoad(self.directory, zone)
                    # if request.doLoad(self.directory, zone)==1:
                    # self.layerCount += 1


###########################################
    @staticmethod
    def parseXML(XMLMenuElement):
        """ Create a LayerGroup from data in the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"

        quite = False

        layerGroup = LayerGroup()
        layerGroup.title = Tools.getAttributeFromElement(XMLMenuElement, "title")
        layerGroup.directory = Tools.getAttributeFromElement(XMLMenuElement, "directory")
        layerGroup.zones = Tools.getAttributeFromElement(XMLMenuElement, "zones")
        for child in XMLMenuElement:
            tag = child.tag.lower().lstrip("q")
            if (tag == "load_imagery"):
                li = LoadImagery.parseXML(child)
                if li is None:
                    Tools.logError("Menu Error: Bad LoadImagery found in " +
                                   layerGroup.title)
                else:
                    layerGroup.addLoadImagery(li)

            elif (tag == "load_gdb"):
                quite = True
                layerGroup.quite = True

            else:
                Tools.logError("Menu Error: unknown xml element " + tag)

        if layerGroup.isValid():
            return layerGroup
        else:
            return None
