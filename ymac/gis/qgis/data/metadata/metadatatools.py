
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import os
import sys
import qgis.utils
from qgis.core import *
from ...tools import Tools


qgisTools2Folder = os.path.join(os.path.dirname(__file__), ("../../../../.."))
resourcesFolder = os.path.normpath(qgisTools2Folder) + r"/resources"
sys.path.append(resourcesFolder)
try:
    from lxml import etree as ET
    # Tools.debug("running with 32-bit lxml folder")
except ImportError:
    if os.path.isdir(resourcesFolder + r"\lxml64"):
        os.rename(resourcesFolder + r"\lxml", resourcesFolder + r"\lxml32")
        os.rename(resourcesFolder + r"\lxml64", resourcesFolder + r"\lxml")
    elif os.path.isdir(resourcesFolder + r"\lxml32"):
        os.rename(resourcesFolder + r"\lxml", resourcesFolder + r"\lxml64")
        os.rename(resourcesFolder + r"\lxml32", resourcesFolder + r"\lxml")
    try:
        from lxml import etree as ET
        # Tools.debug("running with 64-bit lxml folder")
        # sys.path.remove(os.path.dirname(__file__) + r"\lxml_64bit")
        # sys.path.append(os.path.dirname(__file__)) #+ r"\lxml_32bit")
        # from lxml import etree as ET
        # Tools.debug("running with 32 bit folder")
        # from ......lxml import etree as ET
        # Tools.debug("running with lxml.etree")
    except ImportError:
        try:
            import xml.etree.cElementTree as ET
            Tools.debug("running with cElementTree on Python 2.5+")
        except ImportError:
            try:
                import xml.etree.ElementTree as ET
                # Tools.debug("running with ElementTree on Python 2.5+")
            except ImportError:
                try:
                    # normal cElementTree install
                    import cElementTree as ET
                    # Tools.debug("running with cElementTree")
                except ImportError:
                    try:
                        # normal ElementTree install
                        import elementtree.ElementTree as ET
                        # Tools.debug("running with ElementTree")
                    except ImportError:
                        Tools.debug("Failed to import ElementTree from any known place")


class MetadataTools:

    @staticmethod
    def getExistingMetadataFileLocation(source):    # checked and working
        if isinstance(source, QgsMapLayer):
            layerSource = source.source()
        elif isinstance(source, str):
            layerSource = source
        elif isinstance(source, QString):
            Tools.debug("getExistingMetadataFileLocation converting QString to str")
            return MetadataTools.getExistingMetadataFileLocation(str(source))
        else:
            Tools.debug("getExistingMetadataFileLocation Attribute type error:" +
                        str(type(source)))

        xmlLocation = layerSource + ".xml"
        if not os.path.isfile(xmlLocation):
            if layerSource[-4] == ".":
                xmlLocation = layerSource[:-4] + ".xml"
                if not os.path.isfile(xmlLocation):
                    return None
        return str(xmlLocation)

# ############################################################################
    @staticmethod
    def openMetadataFile(source=None):
        if source is None:
            source = MetadataTools.getExistingMetadataFileLocation(Tools.iface.activeLayer())
        elif isinstance(source, QgsMapLayer):
            source = MetadataTools.getExistingMetadataFileLocation(source)

        if source is None:
            Tools.debug("Unable to locate the metadata file.", "Metadata Error")
            return None
        try:
                openFile = open(source, "r+")   # r+ = read-write
                return openFile
        except:
            Tools.debug("Unable to open metadata file for editing.\n" +
                        "Please check your write privileges for location:\n" +
                        source, "Metadata Error")
            return None

# ############################################################################
    @staticmethod
    def treeToString(tree):
        from lxml import etree as ET
        return ET.tostring(tree)

# ############################################################################
    @staticmethod
    def getMetadataAsHtml(xslLocation, xmlLocation):
        from lxml import etree as ET

        xmltree = MetadataTools.getMetadataAsTree(xmlLocation)
        if xmltree is None:
            return

        try:
            xsltree = ET.parse(xslLocation)
            transform = ET.XSLT(xsltree)
            result = transform(xmltree)
            txt = str(result)
            txt = txt.replace("\n", "")
            return txt
        except:
            Tools.debug("A problem has been encountered parsing:\n" +
                        xslLocation + ".", "Style Sheet Error")
            return

# ############################################################################
    @staticmethod
    def getMetadataAsTree(param):
        from lxml import etree as ET
        if param is None:
            Tools.debug("getMetadataAsTree attrib is None!")
        # handle param as file
        if type(param) is file:
            try:
                xmltree = ET.fromstring(param.read())
                return xmltree
            except:
                Tools.debug("A problem has been encountered parsing:\n" +
                            param.name + ".", "Metadata Error")
                return None
        # handle param as None
        if isinstance(param, QgsMapLayer):
            param = MetadataTools.getExistingMetadataFileLocation(param)
        if param is None:
            Tools.debug("Unable to locate metadata for current layer.",
                        "Metadata Error")
            return
        # handle param as string
        try:
            xmltree = ET.parse(str(param))
            return xmltree
        except:
            Tools.debug("A problem has been encountered parsing:\n" +
                        param + ".", "Metadata Error")
            return None
