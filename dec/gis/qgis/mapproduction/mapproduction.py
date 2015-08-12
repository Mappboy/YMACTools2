from qgis.core import *
from qgis.gui import *
import qgis.utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtXml import *

from ..tools import *
from ..data.metadata.metadatatools import MetadataTools
import os
import shutil
from ..data.crs.crshelper import CRSHelper
from ..data.requests.loadShapefile import LoadShapefile
from ..data.requests.loadImagery import LoadImagery
from datetime import datetime
from ..data.crs.crshelper import CRSHelper
import sys
# sys.path.append(r"C:\Python27\Lib\site-packages\pydev")    #This is actualy the 32-bit version
# import pydevd
#


class MapLabelDialog(QDialog):
    _composerTitle = ""
    _template = ""
    _mapTitle = ""
    _showGrid = False
    _gridStyle = "Solid"
    _showGrat = False
    _gratStyle = "Cross"
    _author = ""
    _jobRef = ""
    _dept = "Yamatji Marlpa Aboriginal Corporation"
    _acro = "YMAC"
    _date = ""
    _time = ""

    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)
        # validate
        self.setupDialog()
        self.result = self.exec_()

    def setupDialog(self):
        self.setMinimumWidth(380)
        self.setWindowTitle("Map Production")
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        from datetime import datetime
        now = datetime.now()

        # Set fonts
        boldFont = QFont()
        boldFont.setWeight(90)
        semiBoldFont = QFont()
        semiBoldFont.setWeight(63)
        normalFont = QFont()
        normalFont.setWeight(50)

# COMPOSER PROPERTIES GROUP
        composerPropertiesGroupBox = QGroupBox("COMPOSER PROPERTIES", self)
        composerPropertiesGroupBox.setFont(boldFont)
        mainLayout.addWidget(composerPropertiesGroupBox)
        composerPropertiesLayout = QFormLayout()
        composerPropertiesGroupBox.setLayout(composerPropertiesLayout)
        self.composerTitleLineEdit = QLineEdit("", self)
        self.composerTitleLineEdit.setFont(normalFont)
        self.composerTitleLabel = QLabel("Composer Title\n(optional)")
        self.composerTitleLabel.setFont(normalFont)
        composerPropertiesLayout.addRow(self.composerTitleLabel, self.composerTitleLineEdit)

    # Page Size Group
        pageSizeGroupBox = QGroupBox("Page Size", self)
        pageSizeGroupBox.setFont(semiBoldFont)
        composerPropertiesLayout.addWidget(pageSizeGroupBox)
        pageSizeLayout = QHBoxLayout()
        pageSizeGroupBox.setLayout(pageSizeLayout)

        # A5 Radio Button
        self.a5RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a5RadioButton)
        self.a5RadioButton.setFont(normalFont)
        self.a5RadioButton.setText("A5")
        if Tools.lastPageSize == "A5":
            self.a5RadioButton.setChecked(True)
        else:
            self.a5RadioButton.setChecked(False)

        # A4 Radio Button
        self.a4RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a4RadioButton)
        self.a4RadioButton.setFont(normalFont)
        self.a4RadioButton.setText("A4")
        if Tools.lastPageSize == "A4":
            self.a4RadioButton.setChecked(True)
        else:
            self.a4RadioButton.setChecked(False)

        # A3 Radio Button
        self.a3RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a3RadioButton)
        self.a3RadioButton.setFont(normalFont)
        self.a3RadioButton.setText("A3")
        if Tools.lastPageSize == "A3":
            self.a3RadioButton.setChecked(True)
        else:
            self.a3RadioButton.setChecked(False)

        # A2 Radio Button
        self.a2RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a2RadioButton)
        self.a2RadioButton.setFont(normalFont)
        self.a2RadioButton.setText("A2")
        if Tools.lastPageSize == "A2":
            self.a2RadioButton.setChecked(True)
        else:
            self.a2RadioButton.setChecked(False)

        # A1 Radio Button
        self.a1RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a1RadioButton)
        self.a1RadioButton.setFont(normalFont)
        self.a1RadioButton.setText("A1")
        if Tools.lastPageSize == "A1":
            self.a1RadioButton.setChecked(True)
        else:
            self.a1RadioButton.setChecked(False)

        # A0 Radio Button
        self.a0RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a0RadioButton)
        self.a0RadioButton.setFont(normalFont)
        self.a0RadioButton.setText("A0")
        if Tools.lastPageSize == "A0":
            self.a0RadioButton.setChecked(True)
        else:
            self.a0RadioButton.setChecked(False)

    # Orientation Group
        orientationGroupBox = QGroupBox("Orientation", self)
        orientationGroupBox.setFont(semiBoldFont)
        composerPropertiesLayout.addWidget(orientationGroupBox)
        orientationLayout = QHBoxLayout()
        orientationGroupBox.setLayout(orientationLayout)

        # Landscape Radio Button
        self.landscapeRadioButton = QRadioButton(self)
        orientationLayout.addWidget(self.landscapeRadioButton)
        self.landscapeRadioButton.setFont(normalFont)
        self.landscapeRadioButton.setText("Landscape")
        if Tools.lastPageOrientation == "Landscape":
            self.landscapeRadioButton.setChecked(True)
        else:
            self.landscapeRadioButton.setChecked(False)

        # Portrait Radio Button
        self.portraitRadioButton = QRadioButton(self)
        orientationLayout.addWidget(self.portraitRadioButton)
        self.portraitRadioButton.setFont(normalFont)
        self.portraitRadioButton.setText("Portrait")
        if Tools.lastPageOrientation == "Portrait":
            self.portraitRadioButton.setChecked(True)
        else:
            self.portraitRadioButton.setChecked(False)

# GRIDS GROUP
        gridsGroupBox = QGroupBox("COORDINATE GRIDS", self)
        gridsGroupBox.setFont(boldFont)
        mainLayout.addWidget(gridsGroupBox)
        gridsLayout = QFormLayout()
        gridsGroupBox.setLayout(gridsLayout)

    # Grid Group
        # Only show if using a projected CRS
        canvas = qgis.utils.iface.mapCanvas()
        gcs = canvas.mapSettings().destinationCrs().geographicFlag()
        gridGroupBox = QGroupBox("Eastings / Northings", self)
        gridGroupBox.setFont(semiBoldFont)
        if not gcs:
            gridsLayout.addWidget(gridGroupBox)
        else:
            gridGroupBox.resize(0, 0)
        gridLayout = QHBoxLayout()
        gridGroupBox.setLayout(gridLayout)

        # 'No Grid' Radio Button
        self.noGridRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.noGridRadioButton)
        self.noGridRadioButton.setFont(normalFont)
        self.noGridRadioButton.setText("No grid")
        self.noGridRadioButton.setChecked(False)

        # 'Lines' Radio Button
        self.linesRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.linesRadioButton)
        self.linesRadioButton.setFont(normalFont)
        self.linesRadioButton.setText("Lines")
        self.linesRadioButton.setChecked(True)

        # 'Crosses' Radio Button
        self.crossesRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.crossesRadioButton)
        self.crossesRadioButton.setFont(normalFont)
        self.crossesRadioButton.setText("Crosses")
        self.crossesRadioButton.setChecked(False)

        # 'Coords' Radio Button
        self.gridCoordsRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.gridCoordsRadioButton)
        self.gridCoordsRadioButton.setFont(normalFont)
        self.gridCoordsRadioButton.setText("Coords only")
        self.gridCoordsRadioButton.setChecked(False)

    # Graticule Group
        gratGroupBox = QGroupBox("Lats / Longs", self)
        gratGroupBox.setFont(semiBoldFont)
        gridsLayout.addWidget(gratGroupBox)
        gratLayout = QHBoxLayout()
        gratGroupBox.setLayout(gratLayout)

        # 'No Grat' Radio Button
        self.noGratRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.noGratRadioButton)
        self.noGratRadioButton.setFont(normalFont)
        self.noGratRadioButton.setText("No grid")
        self.noGratRadioButton.setChecked(False)

        # 'Lines' Radio Button
        self.gratLinesRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.gratLinesRadioButton)
        self.gratLinesRadioButton.setFont(normalFont)
        self.gratLinesRadioButton.setText("Lines")
        self.gratLinesRadioButton.setChecked(False)

        # 'Crosses' Radio Button
        self.gratCrossesRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.gratCrossesRadioButton)
        self.gratCrossesRadioButton.setFont(normalFont)
        self.gratCrossesRadioButton.setText("Crosses")
        self.gratCrossesRadioButton.setChecked(True)

        # 'Coords' Radio Button
        self.gratCoordsRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.gratCoordsRadioButton)
        self.gratCoordsRadioButton.setFont(normalFont)
        self.gratCoordsRadioButton.setText("Coords only")
        self.gratCoordsRadioButton.setChecked(False)

# MAP TEXT GROUP
        mapDetailsGroupBox = QGroupBox("MAP TEXT", self)
        mapDetailsGroupBox.setFont(boldFont)
        mainLayout.addWidget(mapDetailsGroupBox)
        mapDetailsLayout = QFormLayout()
        mapDetailsGroupBox.setLayout(mapDetailsLayout)
        self.mapTitleLineEdit = QLineEdit(MapLabelDialog._mapTitle, self)
        self.mapTitleLineEdit.setFont(normalFont)
        self.authorLineEdit = QLineEdit(MapLabelDialog._author, self)
        self.authorLineEdit.setFont(normalFont)
        self.jobRefLineEdit = QLineEdit(MapLabelDialog._jobRef, self)
        self.jobRefLineEdit.setFont(normalFont)
        self.departmentLineEdit = QLineEdit(MapLabelDialog._dept, self)
        self.departmentLineEdit.setFont(normalFont)
        self.acronymLineEdit = QLineEdit(MapLabelDialog._acro, self)
        self.acronymLineEdit.setFont(normalFont)
        self.dateLineEdit = QLineEdit(now.strftime("%B ") + now.strftime("%d, %Y").lstrip("0"), self)
        self.dateLineEdit.setFont(normalFont)
        self.timeLineEdit = QLineEdit(now.strftime("%I:%M %p").lstrip("0"), self)
        self.timeLineEdit.setFont(normalFont)
        self.mapTitleLabel = QLabel("Map Title")
        self.mapTitleLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.mapTitleLabel, self.mapTitleLineEdit)
        self.authorLabel = QLabel("Author")
        self.authorLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.authorLabel, self.authorLineEdit)
        self.jobRefLabel = QLabel("Job Reference")
        self.jobRefLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.jobRefLabel, self.jobRefLineEdit)
        self.deptLabel = QLabel("Department")
        self.deptLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.deptLabel, self.departmentLineEdit)
        self.acronymLabel = QLabel("Acronym")
        self.acronymLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.acronymLabel, self.acronymLineEdit)
        self.dateLabel = QLabel("Date")
        self.dateLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.dateLabel, self.dateLineEdit)
        self.timeLabel = QLabel("Time")
        self.timeLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.timeLabel, self.timeLineEdit)

        buttonsLayout = QHBoxLayout()
        mainLayout.addLayout(buttonsLayout)
        self.okButton = QPushButton("Create Map", self)
        self.cancelButton = QPushButton("Cancel", self)
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addWidget(self.cancelButton)

        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def accept(self):
        # validate
        if len(self.mapTitleLineEdit.text()) == 0 or \
           len(self.authorLineEdit.text()) == 0 or \
           len(self.jobRefLineEdit.text()) == 0 or \
           len(self.departmentLineEdit.text()) == 0 or \
           len(self.acronymLineEdit.text()) == 0 or \
           len(self.dateLineEdit.text()) == 0 or \
           len(self.timeLineEdit.text()) == 0:
                Tools.debug("Please complete all Map fields.", "Input Error")
                return


        # save values
        pageSize = ""
        orientation = ""
        showGrid = False
        gridStyle = None
        showGrat = False
        gratStyle = None
        if self.a5RadioButton.isChecked():
            pageSize = "A5"
        elif self.a4RadioButton.isChecked():
            pageSize = "A4"
        elif self.a3RadioButton.isChecked():
            pageSize = "A3"
        elif self.a2RadioButton.isChecked():
            pageSize = "A2"
        elif self.a1RadioButton.isChecked():
            pageSize = "A1"
        elif self.a0RadioButton.isChecked():
            pageSize = "A0"
        if self.landscapeRadioButton.isChecked():
            orientation = "Landscape"
        elif self.portraitRadioButton.isChecked():
            orientation = "Portrait"
        Tools.lastPageSize = pageSize
        Tools.lastPageOrientation = orientation
        if self.noGridRadioButton.isChecked():
            showGrid = False
        else:
            showGrid = True
            if self.linesRadioButton.isChecked():
                gridStyle = QgsComposerMapGrid.Solid
            elif self.crossesRadioButton.isChecked():
                gridStyle = QgsComposerMapGrid.Cross
            elif self.gridCoordsRadioButton.isChecked():
                gridStyle = QgsComposerMapGrid.FrameAnnotationsOnly
        if self.noGratRadioButton.isChecked():
            showGrat = False
        else:
            showGrat = True
            if self.gratLinesRadioButton.isChecked():
                gratStyle = QgsComposerMapGrid.Solid
            elif self.gratCrossesRadioButton.isChecked():
                gratStyle = QgsComposerMapGrid.Cross
            elif self.gratCoordsRadioButton.isChecked():
                gratStyle = QgsComposerMapGrid.FrameAnnotationsOnly


        # COMPOSER TITLE CHECKS
        # Get list of existing composer titles
        composers = Tools.iface.activeComposers()
        composerTitles = []
        for item in composers:
            composerTitles.append(item.composerWindow().windowTitle())
        # If user does not specify title, construct one based on page size and orientation
        if self.composerTitleLineEdit.text() == "":
            i = 1
            string = pageSize + "_" + orientation + "_" + str(i)
            while string in composerTitles:
                i += 1
                string = pageSize + "_" + orientation + "_" + str(i)
            self.composerTitleLineEdit.setText(string)

        else:   #i.e. if user has entered a composer title
            # Check composer title not already in use
            for item in composers:
                if item.composerWindow().windowTitle() == self.composerTitleLineEdit.text():
                    Tools.alert("This project already has a composer with that name.  " +
                                "Please choose another.", "Duplicate Composer Name")
                    self.composerTitleLineEdit.setText("")
                    self.composerTitleLineEdit.setFocus()
                    return


        MapLabelDialog._composerTitle = self.composerTitleLineEdit.text()
        MapLabelDialog._template = "DPAW_" + pageSize + "_" + orientation + ".qpt"
        MapLabelDialog._showGrid = showGrid
        MapLabelDialog._gridStyle = gridStyle
        MapLabelDialog._showGrat = showGrat
        MapLabelDialog._gratStyle = gratStyle
        MapLabelDialog._mapTitle = self.mapTitleLineEdit.text()
        MapLabelDialog._author = self.authorLineEdit.text()
        MapLabelDialog._jobRef = self.jobRefLineEdit.text()
        MapLabelDialog._dept = self.departmentLineEdit.text()
        MapLabelDialog._acro = self.acronymLineEdit.text()
        MapLabelDialog._date = self.dateLineEdit.text()
        MapLabelDialog._time = self.timeLineEdit.text()
        QDialog.accept(self)


class MapProduction(QObject):
    _QGISVersion = float(qgis.core.QGis.QGIS_VERSION[:3])
    qgisTools2Folder = os.path.join(os.path.dirname(__file__), ("../../../.."))
    xMin = None
    xMax = None
    yMin = None
    yMax = None


    def __init__(self):
        QObject.__init__(self, Tools.iface.mainWindow())

    def createMap(self, dlg):
        # Freeze main canvas so it doesn't render changes while map production underway
        canvas = qgis.utils.iface.mapCanvas()
        canvas.freeze(True)

        # import input from user
        composer = dlg._composerTitle
        templateFilename = dlg._template
        title = dlg._mapTitle
        author = dlg._author
        jobRef = dlg._jobRef
        dept = dlg._dept
        acro = dlg._acro

        # create composer from template (based on user-specified page size and orientation)
        template = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/" + templateFilename
        templateFile = file(template, 'rt')
        templateContent = templateFile.read()
        templateFile.close()
        document = QDomDocument()
        document.setContent(templateContent)
        cv = Tools.iface.createNewComposer(composer)

        #Need to get location of scalebar from template file - scalebar moves on loading.
        scaleLocStart = templateContent.find("<ScalebarCentre>") + 16
        scaleLocEnd = templateContent.find("</ScalebarCentre>", scaleLocStart)
        location = templateContent[scaleLocStart:scaleLocEnd]
        comma = location.find(",")
        scalebarX = float(location[:comma])
        scalebarY = float(location[comma + 1:])
        scalebarPosn = QPointF(scalebarX, scalebarY)


        # Initialise progress message
        progressMsg = QMessageBox(QMessageBox.Information, "Step 1 of 2 - should take < 30 sec", u"Loading map template - should take < 30 sec...")
        progressMsg.show()
        # NB Text not working (can only see Heading)

        # Load template
        cv.composition().loadFromTemplate(document)

        # Initialise variables
        if dlg is None:
            return
        maps = []
        mainMap = None
        localityMap = None
        scalebars = []
        images = []
        paper = None
        legend = None
        mainMapLayers = None
        locMapReqd = True

        # other resources
        #crsHelper = CRSHelper(Tools.iface.mapCanvas().mapRenderer().destinationCrs())  #Changed in response to issues Shane had re incorrect proj on map prod - I couldn't replicate
        crsHelper = CRSHelper(Tools.iface.mapCanvas().mapSettings().destinationCrs())
        wellKnownScales = [500, 1000,  2000,  2500, 5000, 7500, 10000, 12500,
                           15000, 20000, 25000, 30000, 40000, 50000, 60000,
                           75000, 80000, 100000, 150000, 200000, 250000, 300000, 400000, 500000,
                           600000, 800000, 1000000, 1250000, 1500000, 1750000, 2000000, 3000000, 4000000, 5000000,
                           6000000, 8000000, 10000000, 12000000, 15000000, 18000000, 20000000, 25000000]

        # get main map, locality map, and legend
        for item in cv.items():
            if type(item) == QgsComposerMap:
                item.setPreviewMode(QgsComposerMap.Rectangle)
                maps.append(item)
            elif type(item) == QgsComposerLegend:
                legend = item

        if len(maps) == 2:
            if maps[0].boundingRect().width() > maps[1].boundingRect().width():
                mainMap = maps[0]
                localityMap = maps[1]
            else:
                mainMap = maps[1]
                localityMap = maps[0]
            global mainMap

        elif len(maps) > 0:
                mainMap = maps[0]
                global mainMap
        else:
            Tools.debug("There is no map in this composer; map production tool will be closed.")
            return
        # keep current layers for main map
        mainMap.storeCurrentLayerSet()
        mainMap.setKeepLayerSet(True)

        # Populate legend then prevent it from automatically changing when inset layers are added
        legend.setAutoUpdateModel(True)
        legend.setAutoUpdateModel(False)

        model = legend.modelV2()
        for r in range(0, model.rowCount()):
            for c in range(0, model.columnCount()):
                if model.index(r,c).data() == "Locality Map Layers":
                    model.removeRows(r, 1)
        legend.updateLegend()
        legend.setLegendFilterByMapEnabled(True)

        # zoom to map canvas extent when composer map is initially created
        canvas = qgis.utils.iface.mapCanvas()
        extent = canvas.extent()
        xMin = canvas.extent().xMinimum()
        xMax = canvas.extent().xMaximum()
        yMin = canvas.extent().yMinimum()
        yMax = canvas.extent().yMaximum()
        canvasRatio = (yMax - yMin)/(xMax - xMin)
        mapRatio = mainMap.rect().height()/mainMap.rect().width()
        if canvasRatio >= mapRatio:
            newXmin = 0.5*(xMin*(1 + canvasRatio/mapRatio) + xMax*(1 - canvasRatio/mapRatio))
            newXmax = 0.5*(xMin*(1 - canvasRatio/mapRatio) + xMax*(1 + canvasRatio/mapRatio))
            newYmin = yMin
            newYmax = yMax
        elif canvasRatio < mapRatio:
            newXmin = xMin
            newXmax = xMax
            newYmin = 0.5*(yMin*(1 + mapRatio/canvasRatio) + yMax*(1 - mapRatio/canvasRatio))
            newYmax = 0.5*(yMin*(1 - mapRatio/canvasRatio) + yMax*(1 + mapRatio/canvasRatio))
        newExtent = QgsRectangle(newXmin, newYmin, newXmax, newYmax)
        mainMap.setNewExtent(newExtent)

        # set to appropriate well known scale
        for scale in wellKnownScales:
            if scale >= mainMap.scale():
                mainMap.setNewScale(scale)
                break


        # Check whether locality map will be required, based on area covered by main map.
        # If main map covers large area cf WA, locality map is set to transparent and no
        # further updates are made to it.

        # if area shown by main map is large relative to area shown by locality map, make locality map transparent.
        mainMapArea = (mainMap.scale()**2) * mainMap.rect().width() * mainMap.rect().height() / 1000000     # in sqm
        if mainMapArea > 2 * 10**12:   # i.e. > 2 million sqkm (approx area of WA is 2.5M sqkm)
            localityMap.setTransparency(100)
            locMapReqd = False
            localityMap.updateItem()


        # iterate through composer items
        for item in cv.items():
            if type(item) == QgsComposerScaleBar:
                # assign scalebar to correct map
                item.setComposerMap(mainMap)
                scalebars.append(item)
            elif type(item) == QgsPaperItem:
                paper = item
            elif type(item) == QgsComposerPicture:
                images.append(item)
            elif type(item) == QgsComposerLabel:
                text = item.text()
                text = text.replace("%T%", title)
                text = text.replace("%DATUM%", crsHelper.datum)
                if crsHelper.projection != "":
                    text = text.replace("%PROJ%", crsHelper.projection)
                else:
                    text = text.replace("Projection: %PROJ%", "Geographic Projection")
                text = text.replace("%A%", author)
                text = text.replace("%DA%", acro)
                text = text.replace("%DEPT%", dept)
                text = text.replace("%J%", jobRef)
                text = text.replace("%TIME%", datetime.now().strftime("%I:%M %p"))
                text = text.replace("%D%", datetime.now().strftime("%B ") + datetime.now().strftime("%d, %Y"))
                item.setText(text)

        # determine Paper Size
        paperSize = ""
        if paper.boundingRect().width() > paper.boundingRect().height():
            orientation = "L"
            longSide = paper.boundingRect().width()
        else:
            orientation = "P"
            longSide = paper.boundingRect().height()
        if longSide < (210 + 5):        # In QGIS 2.x, seems that paper.boundingRect().width() = actual paper size + 4mm
            paperSize = "A5" + orientation
        elif longSide < (297 + 5):
            paperSize = "A4" + orientation
        elif longSide < (420 + 5):
            paperSize = "A3" + orientation
        elif longSide < (594 + 5):
            paperSize = "A2" + orientation
        elif longSide < (841 + 5):
            paperSize = "A1" + orientation
        elif longSide < (1189 + 5):
            paperSize = "A0" + orientation
        else:
            Tools.debug("It looks like you are using an invalid template.", "Invalid Template")
            return

        # reallocate picture source
        for image in images:
            pictureFile = str(image.pictureFile()).rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
            pictureLocation = Tools.getPluginPath() + "resources\\logos\\" + pictureFile
            image.setPictureFile(pictureLocation)

        # UPDATE SCALE BARS, LOCALITY MAP AND GRID(S)
        # First get CRS of canvas and determine if it is projected or geographic
        crs = canvas.mapSettings().destinationCrs()
        # Get grid stack (should be just 'Lat-Long Graticule' and 'East-North Grid' from template)
        eastNorthGrid = None
        latLongGraticule = None
        grids = mainMap.grids()
        for grid in grids.asList():
            if grid.name() == "East-North Grid":
                eastNorthGrid = grid
            elif grid.name() == "Lat-Long Graticule":
                latLongGraticule = grid

        if eastNorthGrid is not None:
            if dlg._showGrid is False or crs.geographicFlag() == True:
                grids.removeGrid(eastNorthGrid.id())
            else:
                MapProduction.updateGrid(mainMap, eastNorthGrid, "East-North Grid", dlg._gridStyle)

        if latLongGraticule is not None:
            if dlg._showGrat is False :
                grids.removeGrid(latLongGraticule.id())
            else:
                MapProduction.updateGrid(mainMap, latLongGraticule, "Lat-Long Graticule", dlg._gratStyle)

        if localityMap is not None and locMapReqd == True:
            MapProduction.createLocalityMap(self, cv, localityMap, mainMap)
            localityMap.updateItem()
        MapProduction.updateScaleBars(mainMap, scalebars, scalebarPosn, paperSize)
        try:
            mainMap.extentChanged.connect(lambda: MapProduction.updateScaleBars(mainMap, scalebars, scalebarPosn, paperSize))
            mainMap.extentChanged.connect(lambda: MapProduction.updateLocalityMap(self, cv, localityMap, mainMap))
        except:
            return

        # Open composer and zoom to its full extent.
        progressMsg.setWindowTitle("Step 2 of 2 - may take a minute")
        progressMsg.setText("Displaying final composer - may take a minute if you have WMS or imagery layers")
        cv.composerWindow().findChild(QAction, "mActionZoomAll").trigger()
        mainMap.setPreviewMode(QgsComposerMap.Render)
        mainMap.updateItem()
        if localityMap is not None and locMapReqd == True:
            localityMap.setPreviewMode(QgsComposerMap.Render)
            localityMap.updateItem()
        canvas.freeze(False)

    @staticmethod
    def createLocalityMap(self, cv, localityMap, mainMap):
        # SETTINGS
        localityMap.setTransparency(0)
        localityMap.setPreviewMode(QgsComposerMap.Render)

        # GET AREA AND CENTROID OF MAIN MAP
        mainMapXMax = mainMap.extent().xMaximum()
        mainMapXMin = mainMap.extent().xMinimum()
        mainMapYMax = mainMap.extent().yMaximum()
        mainMapYMin = mainMap.extent().yMinimum()
        mainMapWidth = mainMapXMax - mainMapXMin
        mainMapHeight = mainMapYMax - mainMapYMin
        mainMapArea = mainMapWidth * mainMapHeight
        mainMapCentreX = (mainMapXMax + mainMapXMin) / 2
        mainMapCentreY = (mainMapYMax + mainMapYMin) / 2
        centroid = QgsPoint(mainMapCentreX, mainMapCentreY)


        # CREATE IN-MEMORY LAYER HOLDING JUST THE CENTROID - MAY NEED TO USE THIS IN LOCALITY MAP
        # First check whether such a layer already exists, and if so, remove it.
        layers = qgis.utils.iface.legendInterface().layers()
        mapCRS = Tools.iface.mapCanvas().mapSettings().destinationCrs()
        for layer in layers:
            if layer.name() == "__LAYER5":
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        # Create layer
        centroidLayer = QgsVectorLayer("Point?crs=" + mapCRS.toWkt(), "__LAYER5", "memory")
        memoryProvider = centroidLayer.dataProvider()
        # Create feature
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPoint(centroid))
        memoryProvider.addFeatures([feature])
        # Transform CRS if need be - need centroid Lat/Long for deciding whether in SW zone for locality layers.
        if mapCRS.geographicFlag() == False:
            gda94 = QgsCoordinateReferenceSystem(4283)
            xform = QgsCoordinateTransform(mapCRS, gda94)
            centroid = QgsPoint(xform.transform(centroid))


        # CHECK WHETHER LOCALITY MAP LAYERS ARE IN PLACE; IF NOT, ADD THEM TO THE CANVAS.
        dataLegend = qgis.utils.iface.legendInterface()
        if "Locality Map Layers" not in dataLegend.groups():
            localityLayers = dataLegend.addGroup("Locality Map Layers")
            dataLegend.setGroupVisible(localityLayers, False)
            dataLegend.setGroupExpanded(localityLayers, False)


            # State boundary - no labels required
            stateBoundary = LoadShapefile.loadShapefile(r"\Hydrography\State\WA_coast_smoothed.shp", "__LAYER1")
            stateBoundaryQml = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/wa_inset_style.qml"
            stateBoundary.loadNamedStyle(stateBoundaryQml)
            if stateBoundary is not None:
                QgsMapLayerRegistry.instance().addMapLayer(stateBoundary)
                dataLegend.moveLayer(stateBoundary, localityLayers)
                dataLegend.setLayerVisible(stateBoundary, False)

            # regions layer with labels
            regions = LoadShapefile.loadShapefile(r"\Administration_Boundaries\State\dec_regions.shp", "__LAYER2")
            if regions is not None:
                QgsMapLayerRegistry.instance().addMapLayer(regions)
                dataLegend.moveLayer(regions, localityLayers)
                dataLegend.setLayerVisible(regions, False)
                palyr = QgsPalLayerSettings()
                palyr.readFromLayer(regions)
                palyr.enabled = True
                palyr.fieldName = 'REGION'
                palyr.writeToLayer(regions)

            # LGA layer with labels
            lgas = LoadShapefile.loadShapefile(r"\Administration_Boundaries\State\local_gov_authority.shp", "__LAYER3")
            if lgas is not None:
                QgsMapLayerRegistry.instance().addMapLayer(lgas)
                dataLegend.moveLayer(lgas, localityLayers)
                dataLegend.setLayerVisible(lgas, False)
                lgaQml = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/lga_style.qml"
                lgas.loadNamedStyle(lgaQml)

            # Localities layer with labels
            localities = LoadShapefile.loadShapefile(r"\Administration_Boundaries\State\locality_boundary.shp", "__LAYER4")
            if localities is not None:
                QgsMapLayerRegistry.instance().addMapLayer(localities)
                dataLegend.moveLayer(localities, localityLayers)
                dataLegend.setLayerVisible(localities, False)
                palyr = QgsPalLayerSettings()
                palyr.readFromLayer(localities)
                palyr.enabled = True
                palyr.fieldName = 'LOC_NAME'
                palyr.writeToLayer(localities)

        # Centroid layer - always added even if locality layers have alread been created (centroid may be in different place)
        if centroidLayer is not None:
            QgsMapLayerRegistry.instance().addMapLayer(centroidLayer)
            centroidQml = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/centroid_marker.qml"
            centroidLayer.loadNamedStyle(centroidQml)
            groups = qgis.utils.iface.legendInterface().groups()
            for group in groups:
                if group == "Locality Map Layers":
                    groupIndex = groups.index(group)
                    dataLegend.moveLayer(centroidLayer, groupIndex)
                    dataLegend.setLayerVisible(centroidLayer, False)
            # May need error handling for case where no group named "Locality Map Layers" - but this situation would not normally arise


        # STORE EXISTING VISIBILITY SETTINGS THEN CHANGE THEM FOR PREPARATION OF LOCALITY MAP
        # Get list of all layers and their visibility, then set all main map
        # layers to not visible.  Visibility settings for locality map layers will be set later.
        mainMapLayers = []
        layerSet = []
        layers = qgis.utils.iface.legendInterface().layers()    # Need to re-do as layers may have changed with new __LAYER5
        for layer in layers:
            isVisible = qgis.utils.iface.legendInterface().isLayerVisible(layer)
            mainMapLayers.append((layer.id(), isVisible))
            if layer.name()[:7] == "__LAYER":
                layerSet.append(layer.id()) #Fills layerSet with ALL potential locality map layers - will be filtered later.
            else:
                qgis.utils.iface.legendInterface().setLayerVisible(layer, False)


        # GET FULL EXTENT OF POTENTIAL LOCALITY MAP LAYERS
        xMins = []
        xMaxs = []
        yMins = []
        yMaxs = []

        settings = QgsMapSettings()     # Require QGIS >= 2.4 for this
        settings.setCrsTransformEnabled(True)
        settings.setLayers(layerSet)
        settings.setDestinationCrs(Tools.iface.mapCanvas().mapSettings().destinationCrs())
        for layer in layers:
            if layer.id() in layerSet:
                if MapProduction._QGISVersion < 2.4:
                    outputExtent = localityMap.mapRenderer().layerExtentToOutputExtent(layer, layer.extent())
                elif MapProduction._QGISVersion >= 2.4:
                    outputExtent = settings.layerExtentToOutputExtent(layer, layer.extent())
                else:
                    return
                xMins.append(outputExtent.xMinimum())
                xMaxs.append(outputExtent.xMaximum())
                yMins.append(outputExtent.yMinimum())
                yMaxs.append(outputExtent.yMaximum())

        self.xMin = min(xMins)
        self.xMax = max(xMaxs)
        self.yMin = min(yMins)
        self.yMax = max(yMaxs)

        xMin = self.xMin    # Only purpose of these 4 lines is to make later code more readable.
        xMax = self.xMax
        yMin = self.yMin
        yMax = self.yMax


        # SET INITIAL EXTENT OF LOCALITY MAP, AND AREA COVERED BY IT.
        # Initial extent is full extent of locality layers plus a 20% buffer.
        locMapExtent = QgsRectangle(xMin, yMin, xMax, yMax)
        locMapExtent.scale(1.2)
        localityMap.zoomToExtent(locMapExtent)
        locMapWidth = localityMap.extent().xMaximum() - localityMap.extent().xMinimum()
        locMapHeight = localityMap.extent().yMaximum() - localityMap.extent().yMinimum()
        locMapArea = locMapWidth * locMapHeight

        #IF MAIN MAP WILL SHOW AS < 1% OF MAIN MAP, PAN AND ZOOM TO SECTOR CONTAINING CENTROID
        while mainMapArea / locMapArea < 0.01:
            # Define a 4 x 4 grid within the locality map, and find which 2 x 2 grid within this has its centroid closest to main map centroid.
            # Then zoom into that area (equal to the appropriate 2 x 2 grid).
            extent = localityMap.extent()
            xMin = extent.xMinimum()
            xMax = extent.xMaximum()
            yMin = extent.yMinimum()
            yMax = extent.yMaximum()
            x1 = xMin + (xMax - xMin)/4
            y1 = yMin + (yMax - yMin)/4
            x2 = xMin + (xMax - xMin)/2
            y2 = yMin + (yMax - yMin)/2
            x3 = xMax - (xMax - xMin)/4
            y3 = yMax - (yMax - yMin)/4
            if mainMapCentreX <= (x1 + x2)/2:
                newXMin = xMin
                newXMax = x2
            elif mainMapCentreX <= (x2 + x3)/2:
                newXMin = x1
                newXMax = x3
            else:
                newXMin = x2
                newXMax = xMax
            if mainMapCentreY <= (y1 + y2)/2:
                newYMin = yMin
                newYMax = y2
            elif mainMapCentreY <= (y2 + y3)/2:
                newYMin = y1
                newYMax = y3
            else:
                newYMin = y2
                newYMax = yMax
            newExtent = QgsRectangle(newXMin, newYMin, newXMax, newYMax)
            localityMap.zoomToExtent(newExtent)
            locMapArea = (newXMax - newXMin) * (newYMax - newYMin)


        # CHOICE OF LOCALITY MAP LAYERS WILL VARY WITH LOCATION (IN OR OUT OF SW CORNER) AND SIZE OF AREA COVERED BY LOCALITY MAP
        # Get approx area of locality map in sqm - locMapArea already holds this if CRS is in metres.  If CRS is geographic:
        if mapCRS.geographicFlag() == True:
            mga51 = QgsCoordinateReferenceSystem(28351)     # MGA 51 used as a convenient proxy
            xform = QgsCoordinateTransform(mapCRS, mga51)
            projectedExtent = QgsRectangle(xform.transform(localityMap.extent()))
            locMapArea = projectedExtent.height() * projectedExtent.width()
        visibleLayers = []
        if centroid.x() < 119 and centroid.y() < -30:   # i.e. in SW section (larger than SW region)        NB could change these to 'Constants'
            # List layers to be made visible (excluding centroid layer at this stage)
            if locMapArea <= 5*10**7:
                visibleLayers = ["__LAYER1", "__LAYER4"]    # WA boundary + localities
            elif locMapArea <= 5*10**9:
                visibleLayers = ["__LAYER1", "__LAYER3"]    # WA boundary + LGAs
            else:
                visibleLayers = ["__LAYER1", "__LAYER2"]    # WA boundary + DPAW Regions
        else:
            if locMapArea <= 5*10**8:
                visibleLayers = ["__LAYER1", "__LAYER4"]    # WA boundary + localities
            elif locMapArea <= 5*10**10:
                visibleLayers = ["__LAYER1", "__LAYER3"]    # WA boundary + LGAs
            else:
                visibleLayers = ["__LAYER1", "__LAYER2"]    # WA boundary + DPAW Regions

        # Set layers for locality map
        for layer in layers:
            if layer.name()in visibleLayers:
                qgis.utils.iface.legendInterface().setLayerVisible(layer, True)
            else:
                if layer.id() in layerSet:
                    layerSet.remove(layer.id())
        localityMap.setLayerSet(layerSet)
        localityMap.setKeepLayerSet(True)

        # RESIZE LOCALITY MAP IF NOT ENOUGH CONTEXT (I.E. TOO FEW BORDERS BETWEEN REGIONS / LGAS / LOCALITIES ARE DISPLAYED
        request = QgsFeatureRequest()
        for layer in layers:
            if layer.name() == "__LAYER2":  # Reset region labels
                palyr = QgsPalLayerSettings()
                palyr.readFromLayer(layer)
                palyr.enabled = True
                palyr.writeToLayer(layer)
            if layer.name() == visibleLayers[1]:
                count = 0
                layerCRS = layer.crs()
                locMapExtent = localityMap.extent()
                j = 0   # Loop counter
                while count < 4:     # i.e. if < 4 polys show in locality map
                    xform = QgsCoordinateTransform(mapCRS, layerCRS)
                    filterRectangle = QgsRectangle(xform.transform(locMapExtent))
                    request.setFilterRect(filterRectangle)
                    i = 0
                    for f in layer.getFeatures(request):
                        i += 1
                        #if i >= 3:
                            #break
                    count = i
                    if count < 4:
                        locMapExtent.scale(1.4)   # Will approximately double the area covered by locality map
                    elif count > 5 and layer.name() == "__LAYER2":  # Tweak to switch off region labels when most or all of WA showing
                        palyr = QgsPalLayerSettings()
                        palyr.readFromLayer(layer)
                        palyr.enabled = False
                        palyr.writeToLayer(layer)
                    j += 1
                if j > 1:
                    localityMap.setNewExtent(locMapExtent)
                    # THIS MAY CAUSE BOX SHOWING MAIN MAP AREA TO DIMINISH TO INVISIBILITY - IF SO SWITCH ON CENTROID LAYER TO INDICATE LOCATION.
                    locMapArea = locMapExtent.width() * locMapExtent.height()
                    if locMapArea / mainMapArea > 400:
                        #add cross at centroid
                        for layer in layers:
                            if layer.name() == "__LAYER5":
                                qgis.utils.iface.legendInterface().setLayerVisible(layer, True)
                                layerSet2 = []
                                layerSet2.append(layer.id())    # Need this (point) as the FIRST layer in the list
                                for oldLayer in layerSet:
                                    layerSet2.append(oldLayer)
                                localityMap.setKeepLayerSet(False)
                                localityMap.setLayerSet(layerSet2)
                                localityMap.setKeepLayerSet(True)

        # ENSURE WA BOUNDARIES ARE NOT TOO FAR FROM EDGE OF MAP - IF NEED BE, PAN MAP
        # Specify min & max Lat/Long - do not want locality map to extend beyond these.
        yMaxWA = -13
        xMaxWA = 132
        yMinWA = -36
        xMinWA = 109

        # Convert loc map extent to GDA94
        if mapCRS.geographicFlag() == False:
            gda94 = QgsCoordinateReferenceSystem(4283)
            xform = QgsCoordinateTransform(mapCRS, gda94)
            inputExtent = QgsRectangle(xform.transform(localityMap.extent()))
        else:
            inputExtent = localityMap.extent()
        xShift = 0
        yShift = 0
        if inputExtent.xMinimum() < xMinWA and inputExtent.xMaximum() <= xMaxWA:
            xShift = xMinWA - inputExtent.xMinimum()
        elif inputExtent.xMaximum() > xMaxWA and inputExtent.xMinimum() >= xMinWA:
            xShift = xMaxWA - inputExtent.xMaximum()
        if inputExtent.yMinimum() < yMinWA and inputExtent.yMaximum() <= yMaxWA:
            yShift = yMinWA - inputExtent.yMinimum()
        elif inputExtent.yMaximum() > yMaxWA and inputExtent.yMinimum() >= yMinWA:
            yShift = yMaxWA - inputExtent.yMaximum()
        gdaXMin = inputExtent.xMinimum() + xShift
        gdaXMax = inputExtent.xMaximum() + xShift
        gdaYMin = inputExtent.yMinimum() + yShift
        gdaYMax = inputExtent.yMaximum() + yShift
        gdaExtent = QgsRectangle(gdaXMin, gdaYMin, gdaXMax, gdaYMax)
        if mapCRS.geographicFlag() == False:
            gda94 = QgsCoordinateReferenceSystem(4283)
            xform = QgsCoordinateTransform(gda94, mapCRS)
            outputExtent = QgsRectangle(xform.transform(gdaExtent))
        else:
            outputExtent = gdaExtent
        localityMap.setNewExtent(outputExtent)



        # SWITCH OFF ALL LOCALITY MAP LAYERS AND RETURN MAINMAP LAYERS' VISIBILITY STATUS TO WHAT THEY WERE BEFORE.
        for layer in layers:
            if layer.name()[:7] == "__LAYER":
                qgis.utils.iface.legendInterface().setLayerVisible(layer, False)
            else:
                for mapLayerInfo in mainMapLayers:
                    if layer.id() == mapLayerInfo[0]:
                        qgis.utils.iface.legendInterface().setLayerVisible(layer, mapLayerInfo[1])
        localityMap.setNewScale(localityMap.scale() + 1)    # Used to refresh locality map and ensure marker / box is displayed
        localityMap.update()


    @staticmethod
    def updateLocalityMap(self, cv, localityMap, mainMap):
        progressMsg = QMessageBox(QMessageBox.Information, "Updating locality map",
                                "Updating locality map in response to change in extent of main map - may take a few moments")
        progressMsg.show()
        #mainMap.update()

        '''# Initial filter for whether locality map is needed
        if mainMap.scale() > 10**7:
            localityMap.setTransparency(100)
            return

        # Check whether locality map has been created - if so, self.xMin etc will not be None
        if self.xMin is None or self.xMax is None or self.yMin is None or self.yMax is None:
            Tools.debug("Creating locality map")
            MapProduction.createLocalityMap(self, cv, localityMap, mainMap)
            return'''


        mainMapArea = (mainMap.scale()**2) * mainMap.rect().width() * mainMap.rect().height() / 1000000     # in sqm (even if canvas in GCS)
        if mainMapArea > 2 * 10**12:   # i.e. > 2 million sqkm (approx area of WA is 2.5M sqkm)
            localityMap.setTransparency(100)
        else:
            MapProduction.createLocalityMap(self, cv, localityMap, mainMap)
        progressMsg.close()


    @staticmethod
    def updateScaleBars(map, scalebars, scalebarPosn, paperSize):     # NB Also updates grids
        #progressMsg = QMessageBox(QMessageBox.Information, "Updating scalebars and grids",
        #                        "Updating scalebars and grids in response to change in extent of main map - may take a few moments")
        #progressMsg.show()
        # analyse scale
        scale = map.scale()

        relScale = scale
        factor = 1.0

        while relScale >= 10:
            relScale /= 10
            factor *= 10

        while relScale < 1:
            relScale *= 10
            factor /= 10

        # adjust scalebars
        for scalebar in scalebars:
            scalebar.setUnits(QgsComposerScaleBar.Meters)
            scalebar.setComposerMap(map)
            Tools.log(scalebar.style())
            if scalebar.style() != "Numeric":
                # scalebar units
                if scale > 40000:
                    scalebar.setNumMapUnitsPerScaleBarUnit(1000)
                    scalebar.setUnitLabeling("km")
                else:
                    scalebar.setNumMapUnitsPerScaleBarUnit(1)
                    scalebar.setUnitLabeling("m")

                # page and scale specific parameters
                if paperSize[:2] == "A0":
                    numSegments = 5
                    scaleRange = 140
                    if relScale > 8.95:
                        barInterval = 0.25
                    elif relScale >= 3.58:
                        barInterval = 0.1
                    elif relScale >= 1.75:
                        barInterval = 0.05
                    else:
                        barInterval = 0.025

                elif paperSize[:2] == "A1":
                    numSegments = 5
                    scaleRange = 100
                    if relScale > 4.66:
                        barInterval = 0.1
                    elif relScale >= 2.36:
                        barInterval = 0.05
                    elif relScale >= 1.16:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                elif paperSize[:2] == "A2":
                    numSegments = 5
                    scaleRange = 70
                    if relScale >= 5.359:
                        barInterval = 0.1
                    elif relScale >= 2.729:
                        barInterval = 0.05
                    elif relScale >= 1.06:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                elif paperSize[:2] == "A3":
                    numSegments = 5
                    scaleRange = 50
                    if relScale >= 7.95:
                        barInterval = 0.1
                    elif relScale >= 3.98:
                        barInterval = 0.05
                    elif relScale >= 1.58:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                elif paperSize[:2] == "A4" or paperSize[:2] == "A5":    # Initial test for A5; may have to change
                    numSegments = 3
                    scaleRange = 30
                    if relScale >= 9.19:
                        barInterval = 0.1
                    elif relScale >= 4.599:
                        barInterval = 0.05
                    elif relScale >= 2.2:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                scalebar.setNumUnitsPerSegment(barInterval * float(factor))

                # apply bar settings
                scalebar.setNumSegments(numSegments)
                scalebar.adjustBoxSize()
                width = scalebar.rect().width()
                while width > scaleRange:
                    numSegments -= 1
                    scalebar.setNumSegments(numSegments)
                    scalebar.adjustBoxSize()
                    width = scalebar.rect().width()
                scalebar.setItemPosition(scalebarPosn.x(), scalebarPosn.y(), QgsComposerItem.Middle)
        # update grid intervals
        for grid in map.grids().asList():
            if grid.name() in ["East-North Grid", "Lat-Long Graticule"]:
                MapProduction.updateGrid(map, grid, grid.name(), grid.style())
        progressMsg = QMessageBox(QMessageBox.Information, "Updating scalebars and grids",
                                "Updating scalebars and grids in response to change in extent of main map - may take a few moments")
        progressMsg.show()
        map.updateCachedImage()
        map.updateItem()
        progressMsg.close()
        return


    @staticmethod
    def updateGrid(mainMap, grid, gridName, gridStyle):
        scale = mainMap.scale()
        # determine relative scale & factor
        relScale = scale
        factor = 1
        eastNorthGrid = None
        latLongGraticule = None
        canvas = qgis.utils.iface.mapCanvas()

        while relScale > 10:
            relScale /= 10
            factor *= 10

        while relScale < 1:
            relScale *= 10
            factor /= 10

        # set grid interval
        if relScale > 7:
            gridInterval = 0.50
        elif relScale > 4:
            gridInterval = 0.25
        elif relScale > 2:
            gridInterval = 0.1
        else:
            gridInterval = 0.05

        if gridName == "East-North Grid":
            # Get canvas's CRS
            crs = canvas.mapSettings().destinationCrs()
            grid.setCrs(crs)
            gridInterval *= factor
            if gridInterval < 1:
                gridInterval = 1.0

        elif gridName == "Lat-Long Graticule":
            # Get canvas's associated GCS
            gcsEPSG = 4283  # default is GDA94
            gcs = canvas.mapSettings().destinationCrs().geographicCRSAuthId()
            if gcs[:4] == "EPSG" and gcs[5:].isnumeric():
                gcsEPSG = int(gcs[5:])
            grid.setCrs(QgsCoordinateReferenceSystem(gcsEPSG, QgsCoordinateReferenceSystem.EpsgCrsId))
            gridInterval *= factor/100000.0
            #get 'precision' of gridInterval, and set annotation precision based on this  (if gridInterval < 1)
            if gridInterval >= 1:
                grid.setAnnotationPrecision(0)
            else:
                if len(str(gridInterval).split(".")) > 1:    # i.e. if grid interval includes decimal point - NB this code is to accommodate e.g. 5 e-05
                    precision = max([len(str(gridInterval).split(".")[1])-3, 0])
                else:
                    precision = int(str(gridInterval).split("e-")[1]) - 4
                grid.setAnnotationPrecision(precision)
        else:   # i.e. if different grid name
            return
        grid.setStyle(gridStyle)
        grid.setIntervalY(gridInterval)
        grid.setIntervalX(gridInterval)
        mainMap.updateItem()
