from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ..tools import Tools
from string import ascii_uppercase


class DataLocationsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)

        self.setWindowTitle("Data Locations")

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        drivesLayout = QFormLayout()
        mainLayout.addLayout(drivesLayout)

        drives = []
        for letter in ascii_uppercase:
            drives.append(letter + ":")

        drive1ComboBox = QComboBox(self)
        self.drive1ComboBox = drive1ComboBox
        target = Tools.getDataDrive1().upper()
        for drive in drives:
            drive1ComboBox.addItem(drive, None)
            if drive == target:
                drive1ComboBox.setCurrentIndex(drive1ComboBox.count() - 1)

        drivesLayout.addRow("Corporate Data Drive:", drive1ComboBox)

        drive2ComboBox = QComboBox(self)
        self.drive2ComboBox = drive2ComboBox
        target = Tools.getDataDrive2().upper()
        for drive in drives:
            drive2ComboBox.addItem(drive, None)
            if drive == target:
                drive2ComboBox.setCurrentIndex(drive2ComboBox.count() - 1)

        drivesLayout.addRow("External Corporate Data Drive:", drive2ComboBox)

        buttonsLayout = QHBoxLayout()
        mainLayout.addLayout(buttonsLayout)

        okButton = QPushButton("OK", self)
        buttonsLayout.addWidget(okButton)
        okButton.setAutoDefault(True)
        okButton.clicked.connect(self.accept)

        cancelButton = QPushButton("Cancel", self)
        buttonsLayout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.reject)

        self.exec_()

    def accept(self):
        QDialog.accept(self)

        d1cb = self.drive1ComboBox
        Tools.setDataDrive1(str(d1cb.itemText(d1cb.currentIndex())))

        d2cb = self.drive2ComboBox
        Tools.setDataDrive2(str(d2cb.itemText(d2cb.currentIndex())))

        Tools.dm.loadMenuData()
