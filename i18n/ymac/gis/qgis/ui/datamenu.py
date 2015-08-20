# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
import os.path
import datetime

import xml.etree.ElementTree as ET

from ..tools import Tools
from ..data.requests.menuItem import MenuItem


class DataMenu:

    ###############################
    def __init__(self, layout):
        # TODO assert treeview
        self.view = QTreeView()
        layout.addWidget(self.view)

        self.view.setUniformRowHeights(True)
        self.view.setHeaderHidden(True)
        self.view.setSelectionMode(QAbstractItemView.NoSelection)
        self.view.setExpandsOnDoubleClick(False)
        self.view.setRootIsDecorated(False)

        # self.view.setAttribute(Qt.WA_NoMousePropagation)
        self.view.pressed.connect(self.handleDataMenuPressed)
        # self.view.clicked.connect(self.handleDataMenuClicked)
        # self.view.activated.connect(self.handleDataMenuActivated)

        self.viewModel = QStandardItemModel()
        self.view.setModel(self.viewModel)

        self.loadMenuData()

    # def loadMenuData(self):    #pre-search version
    def loadMenuData(self, text=""):
        Tools.dataMenuDict = {}
        self.viewModel.clear()

        # load from v drive
        # corpMenuSuccess  = self.parseMenu()    #pre-search version
        corpMenuSuccess = self.parseMenu("", text)

        # check for XP
        userFiles = os.path.expanduser("~")
        if "Users" in userFiles:
            # win7
            userFile = userFiles + "/Documents/" + Tools.menuFileName
        else:
            #xp
            userFile = userFiles + "/My Documents/" + Tools.menuFileName

        personalMenuSuccess = False
        # check file exists
        if os.path.isfile(userFile):
            # personalMenuSuccess = self.parseMenu(userFile)     #pre-search version
            personalMenuSuccess = self.parseMenu(userFile, text)

        if not (corpMenuSuccess or personalMenuSuccess):
            #Tools.logError("Unable to load menu.xml files.\nPlease check your V: drive is mapped or USB drive connected.\nIf these are correct please check the settings under QGIS Tools > Tools > Settings > Data Locations.")
            Tools.debug("Unable to load menu.xml files.\nPlease check your V: drive is mapped or USB drive connected.\nIf these are correct please check the settings under QGIS Tools > Tools > Settings > Data Locations.")
###########################################

    def handleDataMenuPressed(self, index):
        """ Action a MenuItem or expand/collapse a menu branch as required. """
        assert isinstance(index, QModelIndex), "Bad Parameter"

        mouseState = QApplication.mouseButtons()
        if (mouseState == Qt.RightButton):
            index = self.viewModel.index(0, 0)
            self.view.setCurrentIndex(index)
            self.view.collapseAll()
            return

        Tools.cddpTechnique = "menu"
        modelNode = self.viewModel.itemFromIndex(index)

        if (modelNode.columnCount() == 0):
            # menu leaf, will correspond with a menu item
            Tools.selectTopLegendItem()
            menuItem = Tools.dataMenuDict[Tools.getModelNodePath(modelNode)]
            menuItem.doLoad()
            # Tools.checkForOTFReprojection();
        else:
            # menu branch, will correspond with a menu branch
            self.view.setExpanded(index, not self.view.isExpanded(index))
        Tools.flushErrors()


############################################################
    # def parseMenuElement(self, XMLMenuElement, targetModel):    #pre search version
    def parseMenuElement(self, XMLMenuElement, targetModel, text):
        """ Attach a node to the targetModel then populate it with data from the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"
        assert (isinstance(targetModel, QStandardItemModel) or
                isinstance(targetModel, QStandardItem)), "Bad Parameter" + str(type(targetModel))

        modelNode = QStandardItem()
        modelNode.setIcon(Tools.iconFolder)
        targetModel.appendRow(modelNode)
        modelNode.setFlags(Qt.ItemIsEnabled)
        modelNode.setText(Tools.getAttributeFromElement(XMLMenuElement, "TITLE"))

        for child in XMLMenuElement:
            tag = child.tag.lower()
            if tag[0] == "q":
                tag = tag[1:]
            elif tag[0] == "a":
                continue
            if (tag == "menu"):
                # self.parseMenuElement(child,modelNode)    #pre search version
                self.parseMenuElement(child, modelNode, text)
            elif (tag == "item"):
                # MenuItem.parseXML(child,modelNode)    #pre search version
                MenuItem.parseXML(child, modelNode, text)
            else:
                # unknown xml
                Tools.logError("Menu Error: unknown xml element " + tag)

        # validate menu element
        if modelNode.rowCount() == 0:
            # Tools.logError("Menu Error: No children found for " + modelNode.text())
            targetModel.removeRow(targetModel.rowCount() - 1)


########################
    # def parseMenu(self,xmlLocation=""):    #pre search version
    def parseMenu(self, xmlLocation="", text=""):
        noise = False
        if xmlLocation == "":
            xmlLocation = os.path.join(Tools.corpMenuLocation, Tools.menuFileName)

        if xmlLocation != "":
            tree = ET.parse(xmlLocation)
            root = tree.getroot()
            for child in root:
                tag = child.tag.lower()
                if tag[0] == "q":
                    tag = tag[1:]
                elif tag[0] == "a":
                    continue
                if (tag == "menu"):
                    # self.parseMenuElement(child, self.viewModel)    #pre search version
                    self.parseMenuElement(child, self.viewModel, text)
                elif (tag == "item"):
                    # MenuItem.parseXML(child,self.viewModel)         #pre search version
                    MenuItem.parseXML(child, self.viewModel, text)
                    # self.parseMenuElement(child,self.viewModel)
                else:
                    # unknown xml
                    Tools.logError("Menu Error: unknown xml element " + tag)
            if len(text) >= 3:
                self.view.expandAll()
            return True
        else:
            return False
