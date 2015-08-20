from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
import xml.etree.ElementTree as ET
from ...tools import Tools
from .loadShapefile import LoadShapefile


class LoadShapefileTiles():

#####################
    def __init__(self):
        self.title = ""
        self.indexfile = ""
        self.caveat = ""
        self.fieldindex = ""


####################
    def isValid(self):
        """ Validates the LoadShapefileTiles. """
        if (self.title is None or self.indexfile is None or self.fieldindex is None):
            return False
        if (len(self.title) > 0 and len(self.indexfile) > 0 and len(self.fieldindex) > 0):
            return True
        else:
            return False


####################
# Changed for 2.8 as individual layers were not being moved to group - possibly due to multi-threading causing this task to be called 
# before shapefiles in legend - NB Tools.moveLayersToNewGroup no longer called (see procedure immediately below this one)
    def doLoadOLD(self):
        """ Load the shapefiles referred to in the LoadShapeFileTiles"""
        if qgis.utils.iface.mapCanvas().layerCount() == 0:
            Tools.alert("Unable to determine the Map Extents.\n" +
                        "Please load a base layer in order to establish a " +
                        "context (e.g. DPaW regions, WA Coast etc.).",
                        "No data in area")
            return
        indexLayer = LoadShapefile.loadShapefile(self.indexfile)
        if indexLayer is not None:
            indexCRS = indexLayer.crs()
            if hasattr(qgis.utils.iface.mapCanvas(), "mapSettings"):
                canvasCRS = qgis.utils.iface.mapCanvas().mapSettings().destinationCrs()
            else:
                canvasCRS = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
            transform = QgsCoordinateTransform(canvasCRS, indexCRS)
            extentInCanvasCRS = qgis.utils.iface.mapCanvas().extent()
            ecMinPoint = QgsPoint(extentInCanvasCRS.xMinimum(), extentInCanvasCRS.yMinimum())
            ecMaxPoint = QgsPoint(extentInCanvasCRS.xMaximum(), extentInCanvasCRS.yMaximum())
            eiMinPoint = transform.transform(ecMinPoint)
            eiMaxPoint = transform.transform(ecMaxPoint)
            extentInIndexCRS = QgsRectangle(eiMinPoint, eiMaxPoint)
            indexLayer.select(extentInIndexCRS, False)
            shpCount = indexLayer.selectedFeatureCount()
            if shpCount == 0:
                if qgis.utils.iface.mapCanvas().layerCount() > 0:
                    Tools.alert("No dataset tiles are located in the area " +
                                "you are looking at.", "No datasets")
                else:
                    Tools.alert("Unable to determine the Map Extents.\n" +
                                "Please load a base layer in order to " +
                                "establish a context (e.g. DPaW regions, " +
                                "WA Coast etc.)", "No data in area")
                return
            elif shpCount > 9:
                load = Tools.showYesNoDialog("""
There are """ + str(shpCount) + """ individual dataset tiles for the are you are looking at.
Loading these could take quite a long time.

Would you like to continue loading the data?
                    """, "Numerous Dataset Tiles")
                if load is not True:
                    return
            errorCount = 0
            okCount = 0
            for feature in indexLayer.selectedFeatures():
                attributes = feature.attributes()
                shapefile = str(attributes[int(self.fieldindex)-2])
                layer = LoadShapefile.loadShapefile(shapefile)
                if layer is not None:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    okCount += 1
                else:
                    errorCount += 1
            if okCount > 0:
                Tools.moveLayersToNewGroup(self.title, okCount)
                if self.caveat != "" and self.caveat is not None:
                    Tools.alert(self.caveat, "Caveat")
            return True
        else:
            return False
            
####################
    def doLoad(self):
        """ Load the shapefiles referred to in the LoadShapeFileTiles"""
        if qgis.utils.iface.mapCanvas().layerCount() == 0:
            Tools.alert("Unable to determine the Map Extents.\n" +
                        "Please load a base layer in order to establish a " +
                        "context (e.g. DPaW regions, WA Coast etc.)",
                        "No data in area")
            sb = qgis.utils.iface.mainWindow().statusBar()
            sb.showMessage("")
            return
        indexLayer = LoadShapefile.loadShapefile(self.indexfile)
        if indexLayer is not None:
            indexCRS = indexLayer.crs()
            if hasattr(qgis.utils.iface.mapCanvas(), "mapSettings"):
                canvasCRS = qgis.utils.iface.mapCanvas().mapSettings().destinationCrs()
            else:
                canvasCRS = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
            transform = QgsCoordinateTransform(canvasCRS, indexCRS)
            extentInCanvasCRS = qgis.utils.iface.mapCanvas().extent()
            ecMinPoint = QgsPoint(extentInCanvasCRS.xMinimum(), extentInCanvasCRS.yMinimum())
            ecMaxPoint = QgsPoint(extentInCanvasCRS.xMaximum(), extentInCanvasCRS.yMaximum())
            eiMinPoint = transform.transform(ecMinPoint)
            eiMaxPoint = transform.transform(ecMaxPoint)
            extentInIndexCRS = QgsRectangle(eiMinPoint, eiMaxPoint)
            indexLayer.select(extentInIndexCRS, False)
            shpCount = indexLayer.selectedFeatureCount()
            if shpCount == 0:
                if qgis.utils.iface.mapCanvas().layerCount() > 0:
                    Tools.alert("No dataset tiles are located in the area " +
                                "you are looking at.", "No datasets")
                else:
                    Tools.alert("Unable to determine the Map Extents.\n" +
                                "Please load a base layer in order to " +
                                "establish a context (e.g. DPaW regions, " +
                                "WA Coast etc.).", "No data in area")
                sb = qgis.utils.iface.mainWindow().statusBar()
                sb.showMessage("")
                return
            elif shpCount > 9:
                load = Tools.showYesNoDialog("""
There are """ + str(shpCount) + """ individual dataset tiles for the are you are looking at.
Loading these could take quite a long time.

Would you like to continue loading the data?
                    """, "Numerous Dataset Tiles")
                if load is not True:
                    sb = qgis.utils.iface.mainWindow().statusBar()
                    sb.showMessage("")                
                    return
            errorCount = 0
            okCount = 0
            # If there's already a group in the TOC for these tiles, use it; otherwise create new group
            legend = qgis.utils.iface.legendInterface()
            groups = legend.groups()
            groupNumber = None
            i = 0
            for group in groups:
                if group == self.title:
                    groupNumber = i
                    break   # NB if > 1 group with this name, just finds the first.
                i += 1
            if groupNumber is None:
                groupNumber = legend.addGroup(self.title)
            # Find group in layer tree
            root = QgsProject.instance().layerTreeRoot()
            group = root.findGroup(self.title)
            groupLayers = []
            for child in group.children():
                if isinstance(child, QgsLayerTreeLayer):
                    groupLayers.append(child.layerName())
            for feature in indexLayer.selectedFeatures():
                attributes = feature.attributes()
                shapefile = str(attributes[int(self.fieldindex)-2])
                lastBackslash = shapefile.rfind("\\")
                lastForwardSlash = shapefile.rfind("/")
                lastSlash = max([lastBackslash, lastForwardSlash])
                shapefileName = shapefile[lastSlash + 1:-4]     # This will strip directories from start and ".shp" from end - should be same as layer name in TOC
                # Check whether group already had layer of this name
                if shapefileName not in groupLayers:
                    layer = LoadShapefile.loadShapefile(shapefile)
                    if layer is not None:
                        QgsMapLayerRegistry.instance().addMapLayer(layer)
                        legend.moveLayer(layer, groupNumber)
                        okCount += 1
                    else:
                        errorCount += 1
            
            if okCount > 0:
                legend.setGroupExpanded(groupNumber, False)
            #    Tools.moveLayersToNewGroup(self.title, okCount)
                if self.caveat != "" and self.caveat is not None:
                    Tools.alert(self.caveat, "Caveat")
            return True
        else:
            return False

#######################################
    @staticmethod
    def parseXML(XMLMenuElement):
        """ Create a LoadShapefileTiles from data in the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"

        loadShapefileTiles = LoadShapefileTiles()
        loadShapefileTiles.title = Tools.getAttributeFromElement(XMLMenuElement, "title")
        loadShapefileTiles.indexfile = Tools.getAttributeFromElement(XMLMenuElement, "indexfile")
        loadShapefileTiles.fieldindex = Tools.getAttributeFromElement(XMLMenuElement, "field_index")
        loadShapefileTiles.caveat = Tools.getAttributeFromElement(XMLMenuElement, "caveat")
        if loadShapefileTiles.isValid():
            return loadShapefileTiles
        else:
            return None
