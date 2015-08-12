from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXmlPatterns import *
from qgis.core import *

import xml.etree.ElementTree as ET

from ...tools import Tools
import qgis.utils

from .....web.authenticatedurllib import AuthenticatedURLLib
from .....web.tools_network import *
from ...data.wms.wmsserver import *

import urllib2
import base64
import time
from ...ui.progressbar import FileDownloader
from datetime import *


class LoadWMSLayer():

    #######################
    def __init__(self):
        self.layergroup = ""
        self.url = ""
        self.searchstring = ""
        self.layername = ""
        self.user = ""
        self.password = ""
        self.encrypted = ""
        self.title = ""
        self.nametimestamp = None
        self.expiry = None


######################
    def isValid(self):
        """ Validates the LoadWMSLayer. """

        if self.layergroup is None or self.url is None or (self.searchstring is None and self.layername is None):   # or self.user is None or self.password is None:
            return False

        if len(self.layergroup) > 0 and len(self.url) > 0:
            if (self.searchstring is not None) and (len(self.searchstring) > 0):
                return True
            if (self.layername is not None) and (len(self.layername) > 0):
                return True
        return False

############################################
    def doLoad(self, directory="", zone=""):
        """ Loads WMS and attaches the resultant layer to the QgsMapLayerRegistry."""
        Tools.log("doLoad")
        if qgis.utils.iface.mapCanvas().layerCount() == 0:
            Tools.alert("Unable to determine the Map Extents.\n" +
                        "Please load a base layer in order to establish a " +
                        "context (e.g. DEC regions, WA Coast etc.)",
                        "No data in area")
            return
        self.loadWMSLayer()


###########################
    def loadWMSLayer(self):
        # Loads layer from server and returns a QgsRasterLayer containing it.
        Tools.log("loadWMSLayer")
        if self.url in Tools.WMSServerSummaryDict:
            return self.searchServerSummary()
        else:
            self.loadWMSCapabilities()
            return False


#################################
    def loadWMSLayerByName(self):
        Tools.log("loadWMSLayerByName")
        label = ""
        if self.title is None:
            label = self.layergroup + " " + self.layername
        else:
            label = self.title

        connectionString = ""

        if (self.user is not None and len(self.user) > 0) and (self.encrypted is None or len(self.encrypted) == 0):
            connectionString = ("url=" + self.url + "&username=" + self.user +
                                "&password=" + self.password +
                                '&crs=EPSG:4283&format=image/png&styles=&layers=' +
                                self.layername)
        else:
            connectionString = self.url

        #crs = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs().authid()
        crs = qgis.utils.iface.mapCanvas().mapSettings().destinationCrs().authid()

        # validate CRS
        # fallback to LatLong
        if len(self.supportedCRSs) == 0:
            self.doLoad()
        elif crs not in self.supportedCRSs:
            if "EPSG:4283" in self.supportedCRSs:
                crs = "EPSG:4283"
            else:
                crs = self.supportedCRSs[0]

        Tools.log(self.layername)

        layer = QgsRasterLayer(connectionString, label, 'wms')
        if layer.isValid():
            Tools.cddpTechnique = "menu"
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            qgis.utils.iface.mainWindow().statusBar().showMessage("Loading Complete", 1000)
            return True
        else:
            Tools.logError("Problem loading WMS layer " + label + " from\n" + self.url)
            return False


##################################
    @staticmethod
    def parseXML(XMLMenuElement):
        """ Create a LoadImagery from data in the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"

        loadWMSLayer = LoadWMSLayer()
        loadWMSLayer.title = Tools.getAttributeFromElement(XMLMenuElement, "title")
        loadWMSLayer.layergroup = Tools.getAttributeFromElement(XMLMenuElement, "layergroup")
        loadWMSLayer.url = Tools.getAttributeFromElement(XMLMenuElement, "url")
        loadWMSLayer.searchstring = Tools.getAttributeFromElement(XMLMenuElement, "searchstring")
        loadWMSLayer.layername = Tools.getAttributeFromElement(XMLMenuElement, "layername")
        loadWMSLayer.user = Tools.getAttributeFromElement(XMLMenuElement, "user")
        loadWMSLayer.password = Tools.getAttributeFromElement(XMLMenuElement, "password")
        loadWMSLayer.encrypted = Tools.getAttributeFromElement(XMLMenuElement, "encrypted")

        exp = Tools.getAttributeFromElement(XMLMenuElement, "expiry")
        if exp is None:
            loadWMSLayer.expiry = None
        else:
            try:
                loadWMSLayer.expiry = timedelta(hours=float(str(exp)))
            except:
                loadWMSLayer.expiry = None

        if loadWMSLayer.encrypted is not None:
            if len(loadWMSLayer.encrypted) > 0:
                loadWMSLayer.user = ""
                loadWMSLayer.password = ""

        if loadWMSLayer.isValid():
            return loadWMSLayer
        else:
            return None


##################################
    def loadWMSCapabilities(self):
        Tools.log("loadWMSCapabilities")
        url = self.url + "REQUEST=GetCapabilities&SERVICE=WMS"
        url = url.replace("//", "//" + self.user + ":" + self.password + "@")
        manager = QgsNetworkAccessManager.instance()

        request = QNetworkRequest(QUrl(url))
        self.reply = manager.createRequest(QNetworkAccessManager.GetOperation, request)
        self.reply.connect(self.reply, SIGNAL("finished()"), self.downloadFinished)


###############################
    def downloadFinished(self):
        text = self.reply.readAll()
        try:
            root = ET.fromstring(text)
            #Tools.cddpTechnique = "manual"
        except:
            doc = QTextDocument()
            doc.setHtml(str(text))
            text = doc.toPlainText()
            if text is None:
                text = ""
            if len(text) > 0 and (len(self.encrypted) > 0 or (len(self.password) == 0 and len(self.user) == 0)):
                Tools.debug("Invalid network response\n\n" +
                            "Please ensure you have entered the correct " +
                            "username/password.", "WMS Error")
                return
            Tools.debug("Invalid network response:\n" + text + "\n" +
                        "Possible causes include:\n\n" +
                        "1.  Your computer may not be connected to the " +
                        "DPAW network - ensure your blue network cable is " +
                        "plugged into your computer. " +
                        "If yes then call DPAW Helpdesk 9334 0334\n\n" +
                        "2.  You may not be connected to the internet - " +
                        "contact DPAW Helpdesk 9334 0334\n\n" +
                        "3.  The WMS server (" + self.url + ") may be " +
                        "offline.  Contact the GIS Application Section.\n\n" +
                        "4.  QGIS network settings may be mis-configured.  " +
                        "Contact the GIS Applications Section.", "WMS Error")
            return
        for child in root:
            if child.tag.lower() == "capability":
                for child2 in child:
                    if child2.tag.lower() == "layer":
                        Tools.WMSServerSummaryDict[self.url] = WMSServerSummary.fromElement(child2)
                        return self.searchServerSummary()

##################################
    def searchServerSummary(self):
        Tools.log("searchServerSummary")
        summary = Tools.WMSServerSummaryDict[self.url]

        if self.expiry is not None:
            elapsed = datetime.now() - summary.timestamp
            if elapsed >= self.expiry:
                del Tools.WMSServerSummaryDict[self.url]
                self.loadWMSCapabilities()
                return False

        # search by name
        if self.layername is not None and len(self.layername) > 0:
            nodes = [summary]
            while len(nodes) > 0:
                node = nodes.pop(0)
                if self.layername == node.name:
                    self.nametimestamp = datetime.now()
                    self.supportedCRSs = node.referenceSystems
                    return self.loadWMSLayerByName()
                else:
                    for child in node.layers:
                        nodes.append(child)
            Tools.debug("Unable to locate layer on WMS server, please " +
                        "check menu.xml and server layers match.\n"
                        + self.searchstring)
            return
        # search by path
        else:
            tokens = self.searchstring.split("\\")
            child = None
            if len(tokens) > 0:
                if tokens[0] in summary.title:
                    parent = summary
                    tokens = tokens[1:]
                    while len(tokens) > 0:
                        hit = False
                        for child in parent.layers:
                            Tools.log(child.title)
                            if tokens[0] in child.title:
                                hit = True
                                if len(tokens) == 1:
                                    self.layername = child.name
                                    self.nametimestamp = datetime.now()
                                    self.supportedCRSs = child.referenceSystems
                                    Tools.log(self.layername)
                                    return self.loadWMSLayerByName()
                                else:
                                    tokens = tokens[1:]
                                    parent = child
                        if not hit:
                            Tools.debug("Unable to locate layer on WMS " +
                                        "server, please check menu.xml and " +
                                        "server layers match.\n" +
                                        self.searchstring)
                            return
