from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ..tools import Tools
from string import ascii_uppercase


class AboutDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)

        self.setWindowTitle("About QGIS Tools")

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        text = "YMAC Tools\n"
        text += "Version: " + Tools.versionNumber + "\n"
        text += "Release Date: " + Tools.releaseDate + "\n"
        text += "Spatial Team\n"
        text += "Yamatji Marlpa Aboriginal Corporation\n"
        text += """
The QGIS Tools application provides added
functionality so that users may more
effectively view, query and manipulate DPaW
corporate data and project datasets within
QGIS Desktop."""

        mainLayout.addWidget(QLabel(text))
        okButton = QPushButton("OK", self)
        mainLayout.addWidget(okButton)
        okButton.setAutoDefault(True)
        okButton.clicked.connect(self.accept)

        self.exec_()
