from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from ..tools import Tools
from ..data.metadata.metadatatools import MetadataTools

import os.path

import qgis.utils


class MetadataViewerDialog(QDialog):

    def __init__(self, layer):
        assert(isinstance(layer, QgsMapLayer)), "MetadataViewerDialog init attrribute type error"
        QDialog.__init__(self, Tools.QGISApp)
        self.layer = layer
        self.setupDialog()
        self.renderMetadata()
        self.styleComboBox.currentIndexChanged.connect(self.styleSheetChanged)
        self.webView.setFocus(Qt.OtherFocusReason)
        self.exec_()


##############################################################################
    def setupDialog(self):
        self.printer = None
        self.setWindowTitle("View Metadata")
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.styleSheetPath = Tools.getPluginPath() + "resources\stylesheets"
        toolsLayout = QHBoxLayout()
        mainLayout.addLayout(toolsLayout)

        # print toolbar
        menubar = QMenuBar(self)
        toolsLayout.addWidget(menubar)

        printButton = QAction(toolsLayout)
        menubar.addAction(printButton)

        printButton.setIcon(Tools.iconPrinter)
        printButton.setText("Print")
        printButton.triggered.connect(self.printWebView)

        pageSetupButton = QAction(toolsLayout)
        menubar.addAction(pageSetupButton)

        pageSetupButton.setIcon(Tools.iconPageSetup)
        pageSetupButton.setText("Page Setup")
        pageSetupButton.triggered.connect(self.pageSetup)

        # stylesheet selection
        toolsLayout.addWidget(QLabel("<b>Current Style Sheet:</b>"))
        self.styleComboBox = QComboBox(self)
        toolsLayout.addWidget(self.styleComboBox)

        ssdir = QDir(self.styleSheetPath)
        self.styleSheetList = []
        for filepath in ssdir.entryList("*.xsl;*.xslt"):
            if "xsl" in filepath:
                self.styleSheetList.append(str(filepath))

        target = "DPAW.xsl"
        for style in self.styleSheetList:
            self.styleComboBox.addItem(style.split(".")[0], None)
            if style == target:
                self.styleComboBox.setCurrentIndex(self.styleComboBox.count() - 1)

        # webview
        webView = QWebView()
        self.webView = webView
        mainLayout.addWidget(webView)


##############################################################################
    def renderMetadata(self):
        xslLocation = self.styleSheetPath + "\\" + str(self.styleComboBox.currentText()) + ".xsl"
        xmlLocation = MetadataTools.getExistingMetadataFileLocation(self.layer)
        html = MetadataTools.getMetadataAsHtml(xslLocation, xmlLocation)
        self.webView.setHtml(html)


##############################################################################
    def styleSheetChanged(self, index):
        self.renderMetadata()


##############################################################################
    def printWebView(self):
        if self.printer is None:
            self.printer = QPrinter()
        printer = self.printer

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            self.webView.print_(printer)


##############################################################################
    def pageSetup(self):
        if self.printer is None:
            self.printer = QPrinter()
        printer = self.printer

        dialog = QPageSetupDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            # self.webView.print_(printer)
            pass
