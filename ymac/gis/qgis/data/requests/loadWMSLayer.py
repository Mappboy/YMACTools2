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
    getCapabilitiesNetworkReplies = []
    loadWMSLayersWaitingForGetCapabilities = {}
    WMSServerSummaryDict = {}


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


    @property
    def full_url(self):
        url = self.url + "REQUEST=GetCapabilities&SERVICE=WMS"
        url = url.replace("//", "//" + self.user + ":" + self.password + "@")
        return url


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


    def doLoad(self, directory="", zone=""):
        """ Loads WMS and attaches the resultant layer to the QgsMapLayerRegistry."""

        if qgis.utils.iface.mapCanvas().layerCount() == 0:
            Tools.alert("Unable to determine the Map Extents.\n" +
                        "Please load a base layer in order to establish a " +
                        "context (e.g. DEC regions, WA Coast etc.)",
                        "No data in area")
            return
        self.loadWMSLayer()


    def loadWMSLayer(self):
        """ Loads layer from server and returns a QgsRasterLayer containing it. """
        if self.url in LoadWMSLayer.WMSServerSummaryDict:
            result = self.searchServerSummary()
            return result
        else:
            self.loadWMSCapabilities()
            return False


    def loadWMSLayerByName(self):
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

        layer = QgsRasterLayer(connectionString, label, 'wms')
        if layer.isValid():
            Tools.cddpTechnique = "menu"
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            self.removeFromQueue()
            qgis.utils.iface.mainWindow().statusBar().showMessage("Loading Complete", 1000)
            return True
        else:
            Tools.logError("Problem loading WMS layer " + label + " from\n" + self.url)
            return False


    def removeFromQueue(self):
        keys  = LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities.keys()
        for key in keys:
            queue = LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities[key]
            if self in queue:
                queue.remove(self)
                if len(queue) == 0:
                    del LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities[key]


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


    def loadWMSCapabilities(self):
        url = self.full_url

        if url in LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities and len(LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities) > 0:
            LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities[url].append(self)
        else:
            LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities[url] = [self]
            
            ###################################################################
            # This QNetworkAccessManager based approach requires an instance of
            # that with a lifetime spanning the duration of the network transaction.
            # For convenience this has been stored as Tools.net_manager.
            request = QNetworkRequest(QUrl(url))
            reply = Tools.net_manager.get(request)
            reply.connect(reply, SIGNAL("finished()"), self.downloadFinished)
            LoadWMSLayer.getCapabilitiesNetworkReplies.append(reply)
            
            #######################################################################
            # This QgsNetworkAccessManager based approach was fine for qgis 1.8 but
            # had problems with 2.x reporting erroneous network timeout errors.
            # It may become useful when the underlying bug is fixed.
            #
            # manager = QgsNetworkAccessManager.instance()
            # request = QNetworkRequest(QUrl(url))
            # reply = manager.createRequest(QNetworkAccessManager.GetOperation, request)
            # reply.connect(reply, SIGNAL("finished()"), self.downloadFinished)
            # LoadWMSLayer.getCapabilitiesNetworkReplies.append(reply)


    def downloadFinished(self):
        self.proccessGetCapabilitiesQueue()


    def proccessGetCapabilitiesQueue(self):
        for reply in LoadWMSLayer.getCapabilitiesNetworkReplies:
            if reply.isFinished():
                LoadWMSLayer.getCapabilitiesNetworkReplies.remove(reply)
                self.proccessCapabilitiesResponse(reply)
                url = str(reply.url().toString())
                self.proccessLoadWMSLayerQueue(url)


    def proccessLoadWMSLayerQueue(self, url):
        if url in LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities:
            loadWMSLayers = LoadWMSLayer.loadWMSLayersWaitingForGetCapabilities[url]
            indexes = range(len(loadWMSLayers))
            indexes.reverse()
            for i in indexes:
                loadWMSLayer = loadWMSLayers[i]
                loadWMSLayer.doLoad()


    def proccessCapabilitiesResponse(self, reply):
        text = reply.readAll()
        try:
            root = ET.fromstring(text)
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
                        LoadWMSLayer.WMSServerSummaryDict[self.url] = WMSServerSummary.fromElement(child2)


    def searchServerSummary(self):
        summary = LoadWMSLayer.WMSServerSummaryDict[self.url]

        if self.expiry is not None:
            elapsed = datetime.now() - summary.timestamp
            if elapsed >= self.expiry:
                del LoadWMSLayer.WMSServerSummaryDict[self.url]
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
                            if tokens[0] in child.title:
                                hit = True
                                if len(tokens) == 1:
                                    self.layername = child.name
                                    self.nametimestamp = datetime.now()
                                    self.supportedCRSs = child.referenceSystems
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