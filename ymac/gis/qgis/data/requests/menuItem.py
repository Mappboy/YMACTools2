from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import os.path

import qgis.utils
import xml.etree.ElementTree as ET

from ...tools import Tools
from .loadShapefile import LoadShapefile
from .loadImageryTiles import LoadImageryTiles
from .layerGroup import LayerGroup
from .loadImagery import LoadImagery
from .loadShapefileTiles import LoadShapefileTiles
from .loadWMSLayer import LoadWMSLayer


class MenuItem():

#######################
    def __init__(self):
        """ Initialises the required data structures. """
        self.loadShapefiles = list()
        self.loadImagerys = list()
        self.layerGroups = list()
        self.loadShapefileTiles = list()
        self.loadImageryTiles = list()
        self.loadWMSLayers = list()

##################
    def isValid(self):
        """ Returns false if the MenuItem contains no data requests. """
        if ( (len(self.loadShapefiles) == 0) and
             (len(self.loadImagerys) == 0) and
             (len(self.layerGroups) == 0) and
             (len(self.loadShapefileTiles) == 0) and
             (len(self.loadImageryTiles) == 0) and
             (len(self.loadWMSLayers) == 0) ):
        #if len(self.loadImageryTiles) == 0:
            #Tools.debug("NULL ITEM")
            return False
        else:
            return True


#############################################
    def addLoadShapefile(self, loadShapefile):
        """ Appends the loadShapefile to required list """
        assert isinstance(loadShapefile, LoadShapefile), "Bad Parameter"

        if loadShapefile is not None:
            self.loadShapefiles.append(loadShapefile)


#############################################
    def addLoadImagery(self, loadImagery):
        """ Appends the loadImagery to required list """
        assert isinstance(loadImagery, LoadImagery), "Bad Parameter"

        if loadImagery is not None:
            self.loadImagerys.append(loadImagery)


#############################################
    def addLayerGroup(self, layerGroup):
        """ Appends the LayerGroup to required list """
        assert isinstance(layerGroup, LayerGroup), "Bad Parameter"

        if layerGroup is not None:
            self.layerGroups.append(layerGroup)


#############################################
    def addLoadShapefileTiles(self, loadShapefileTiles):
        """ Appends the LoadShapefileTiles to required list """
        assert isinstance(loadShapefileTiles, LoadShapefileTiles), "Bad Parameter"

        if loadShapefileTiles is not None:
            self.loadShapefileTiles.append(loadShapefileTiles)

#############################################
    def addLoadImageryTiles(self, loadImageryTiles):
        """ Appends the LoadImageryTiles to required list """
        assert isinstance(loadImageryTiles, LoadImageryTiles), "Bad Parameter"

        if loadImageryTiles is not None:
            self.loadImageryTiles.append(loadImageryTiles)

#############################################
    def addLoadWMSLayers(self, loadWMSLayer):
        """ Appends the LoadWMSLayer to required list """
        assert isinstance(loadWMSLayer, LoadWMSLayer), "Bad Parameter"

        if loadWMSLayer is not None:
            self.loadWMSLayers.append(loadWMSLayer)
            # extract 'url' and 'layers' from wms layer
            url = loadWMSLayer.url
            layers = loadWMSLayer.layername
            #Tools.WMSinCDDP.append(loadWMSLayer.title)  # Used to assemble list of WMS layers in data menu (on opening QGIS)
            Tools.WMSinCDDP.append((url, layers))
#####################
    def doLoad(self):
        """ Iterates through all data request lists. """
        sb = qgis.utils.iface.mainWindow().statusBar()
        sb.showMessage("Loading data...")
        ok = True
        ok = self.doLoadRequestList(self.loadShapefiles) and ok
        ok = self.doLoadRequestList(self.loadImagerys) and ok
        ok = self.doLoadRequestList(self.layerGroups) and ok
        ok = self.doLoadRequestList(self.loadShapefileTiles) and ok
        ok = self.doLoadRequestList(self.loadImageryTiles) and ok
        ok = self.doLoadRequestList(self.loadWMSLayers) and ok
        if ok:
            sb.showMessage("Loading Complete; Rendering...", 1000)

############################################
    """ Iterates through data request list loading each item. """
    def doLoadRequestList(self,requestList):
        ok = True
        for request in requestList:
            ok = request.doLoad() and ok
        return ok

################################################################################################

    @staticmethod
    def parseXML(XMLMenuElement, targetModel, text):
        """ Attach a MenuItem to the targetModel then populate it with data from the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"
        assert (isinstance(targetModel, QStandardItemModel) or
                isinstance(targetModel, QStandardItem)), "Bad Parameter" + str(type(targetModel))
        quite = False
        ##############
        if text.lower() in Tools.getAttributeFromElement(XMLMenuElement, "TITLE").lower() or text =="":

        #####################
            modelNode = QStandardItem()
            modelNode.setIcon(Tools.iconGlobe)
            targetModel.appendRow(modelNode)
            modelNode.setFlags(Qt.ItemIsEnabled)
            modelNode.setText(Tools.getAttributeFromElement(XMLMenuElement,"TITLE"))
            menuItem = MenuItem()
            for child in XMLMenuElement:
                tag=child.tag.lower()
                if tag[0] == "q":
                    tag = tag[1:]
                elif tag[0] == "a":
                    continue

                if (tag == "load_shapefile"):
                    lsf = LoadShapefile.parseXML(child)
                    if lsf is None:
                        Tools.logError("Menu Error: Bad loadshapefile found in " + modelNode.text())
                    else:
                        menuItem.addLoadShapefile(lsf)

                elif (tag == "load_imagery"):
                    li = LoadImagery.parseXML(child)
                    if li is None:
                        Tools.logError("Menu Error: Bad LoadImagery found in " + modelNode.text())
                    else:
                        menuItem.addLoadImagery(li)

                elif (tag == "layer_group"):
                    lg = LayerGroup.parseXML(child)
                    if lg is None:
                        quite = True
                    else:
                        menuItem.addLayerGroup(lg)

                elif (tag == "load_shapefile_tiles"):
                    lsft = LoadShapefileTiles.parseXML(child)
                    if lsft is None:
                        Tools.logError("Menu Error: Bad LoadShapefileTiles found in " + modelNode.text())
                    else:
                        menuItem.addLoadShapefileTiles(lsft)

                elif (tag == "load_imagery_tiles"):
                    lsft = LoadImageryTiles.parseXML(child)
                    if lsft is None:
                        Tools.logError("Menu Error: Bad LoadImageryTiles found in " + modelNode.text())
                    else:
                        menuItem.addLoadImageryTiles(lsft)

                elif (tag == "load_wms_layer"):
                    lwl = LoadWMSLayer.parseXML(child)
                    if lwl == None:
                        Tools.logError("Menu Error: Bad LoadWMSLayer found in " + modelNode.text())
                    else:
                        menuItem.addLoadWMSLayers(lwl)

                elif (tag == "load_gdb"):
                    quite = True

                elif (tag == "load_orthophotos"):
                    quite = True

                else:
                    Tools.logError("Menu Error: unknown xml element " + tag)

            if menuItem.isValid():
                # TODO: handle hash conflicts
                id = Tools.getModelNodePath(modelNode)
                if id not in Tools.dataMenuDict:
                    Tools.dataMenuDict[id] = menuItem
                else:
                    Tools.logError("Menu Error: duplicate menu path " + id)
                    targetModel.removeRow(targetModel.rowCount()-1)
            else:
                if quite is False:
                    Tools.logError("Menu Error: No data requests found for " + modelNode.text())
                targetModel.removeRow(targetModel.rowCount()-1)
