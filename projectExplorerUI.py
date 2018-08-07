
import os
import sys

try:
  from PySide2.QtCore import * 
  from PySide2.QtGui import * 
  from PySide2.QtWidgets import *
  from PySide2 import __version__
except ImportError:
  from PySide.QtCore import * 
  from PySide.QtGui import * 
  from PySide import __version__

import projectExplorer_core
reload(projectExplorer_core)

core = projectExplorer_core.ExplorerCore()

currentDir = os.path.dirname(__file__).replace("\\", '/')

# TODO: Right click menu, Including Open in explorer
# Create new shot button
# Test in real environment [from Klong]

class ExplorerWindow(QMainWindow):

	def __init__(self, parent = None):
		super(ExplorerWindow, self).__init__(parent)
		self.InitUI()
		self.setupUI()
		self.initConnect()

	def InitUI(self):
		
		self.setWindowTitle = "Nuke project explorer"

		mainWidget = QWidget(self)

		self.menuBar = QMenuBar(self)
		self.settingMenu = QMenu("&Setting", self)
		self.preferenceAction = QAction("&Preference", self, triggered = self.callPrefWindow)
		self.settingMenu.addAction(self.preferenceAction)
		self.helpMenu = QMenu("&Help", self)
		self.openDocument = QAction("&Open Document", self, triggered = self.callDocumentLink)
		self.openRepo = QAction("&Source code", self, triggered = self.callGithubLink)
		self.helpMenu.addAction(self.openDocument)
		self.helpMenu.addAction(self.openRepo)

		self.menuBar.addMenu(self.settingMenu)
		self.menuBar.addMenu(self.helpMenu)

		mainLayout = QVBoxLayout()
		self.headWidget = HeaderWidget(self)
		self.fileWidget = fileWidget(self)

		self.buttonLayout = QHBoxLayout()
		self.saveButton = QPushButton("Save++", self)
		self.openButton = QPushButton("Open", self)
		verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.buttonLayout.addItem(verticalSpacer)
		self.buttonLayout.addWidget(self.saveButton)
		self.buttonLayout.addWidget(self.openButton)
		self.buttonLayout.setStretch(0,1)

		mainWidget.setLayout(mainLayout)
		self.setCentralWidget(mainWidget)

		mainLayout.addWidget(self.headWidget)
		mainLayout.addWidget(self.fileWidget)
		mainLayout.addLayout(self.buttonLayout)
		mainLayout.setStretch(1,1)
		self.setMenuBar(self.menuBar)

	def setupUI(self):
		# Setup
		self.headWidget.projectComboBox.addItems(core.listProjects())
		self.fileWidget.setProject(self.currentProject)

	def initConnect(self):
		self.headWidget.projectComboBox.activated.connect(lambda : self.fileWidget.setProject(self.currentProject))
		self.saveButton.clicked.connect(self.save_OnClicked)
		self.openButton.clicked.connect(self.open_onClicked)
		self.fileWidget.shotListWidget.itemClicked.connect(lambda : self.fileWidget.updateFileList(self.currentProject))

	def save_OnClicked(self):
		savePath = core.saveIncrement(self.currentProject, self.fileWidget.currentShot)

		projectExplorer_core.saveFrame(thumbnailPath = projectExplorer_core.thumbnailPath(savePath))
		self.fileWidget.updateFileList(self.currentProject)

	def open_onClicked(self):
		print self.fileWidget.currentFile
		core.openScript(self.fileWidget.currentFile)

	def callPrefWindow(self):
		print "callPrefWindow"

	def callDocumentLink(self):
		print "callDocumentLink"

	def callGithubLink(self):
		print "callGithubLink"

	@property
	def currentProject(self):
		return self.headWidget.projectComboBox.currentText()

class thumbnailWidget(QWidget):

	placeHolder_path = currentDir + '/image/image_placeholder.jpg'
	placeHolder_pixmap = QPixmap(placeHolder_path)

	def __init__(self, parent= None):
		super(thumbnailWidget, self).__init__(parent)
		

		mainLayout = QVBoxLayout()
		self.thumbnail = QLabel("- place holder -", self)

		mainLayout.addWidget(self.thumbnail)

		self.setLayout(mainLayout)

		self.setThumbnail(self.placeHolder_path)

	def setThumbnail(self, imagepath):

		if not os.path.exists(imagepath):
			imagepath = placeHolder_path

		# pixmap =QPixmap(imagepath)
		
		img = QImage(imagepath)
		scaled_percent = 280.0 / max(img.width(),img.height())
		pixmap = QPixmap(img).scaled(QSize(img.width()*scaled_percent,img.height()*scaled_percent, mode = Qt.SmoothTransformation))
		self.thumbnail.setPixmap(pixmap)

class HeaderWidget(QWidget):

	def __init__(self, parent= None):
		super(HeaderWidget, self).__init__(parent)
		
		mainLayout = QVBoxLayout()

		self.title = QLabel("Nuke Project Explorer", self)
		newfont = QFont("Arial Black", 18) 
		self.title.setFont(newfont)
		self.projectLayout = QHBoxLayout()
		self.projectLabel = QLabel("Project : ", self)
		self.projectComboBox = QComboBox(self)
		verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

		self.projectLayout.addWidget(self.projectLabel)
		self.projectLayout.addWidget(self.projectComboBox)
		self.projectLayout.addItem(verticalSpacer)
		self.projectLayout.setStretch(2,1)

		mainLayout.addWidget(self.title)
		mainLayout.addLayout(self.projectLayout)

		self.setLayout(mainLayout)

class fileWidget(QWidget):

	def __init__(self, parent= None):
		super(fileWidget, self).__init__(parent)
		
		mainLayout = QHBoxLayout()
		ShotLayout = QVBoxLayout()

		self.thumbnailWidget = thumbnailWidget(self)
		self.SequenceLayout = QHBoxLayout()
		self.sequenceComboBox = QComboBox(self)
		self.SequenceLayout.addWidget(QLabel("Sequence : ",self))
		self.SequenceLayout.addWidget(self.sequenceComboBox)
		self.SequenceLayout.setStretch(1,1)

		self.shotListWidget = QListWidget(self)
		self.shotLabelLayout = QHBoxLayout()
		self.addShotButton = QPushButton("+",self)
		self.addShotButton.setMaximumWidth(20)
		verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.shotLabelLayout.addWidget(QLabel(self.tr("Shot : ")))
		self.shotLabelLayout.addItem(verticalSpacer)
		self.shotLabelLayout.addWidget(self.addShotButton)
		self.shotLabelLayout.setStretch(1,1)

		ShotLayout.addWidget(self.thumbnailWidget)
		ShotLayout.addLayout(self.SequenceLayout)
		ShotLayout.addLayout(self.shotLabelLayout)
		ShotLayout.addWidget(self.shotListWidget)
		ShotLayout.setStretch(3,1)

		self.fileListWidget = QListWidget(self)

		mainLayout.addLayout(ShotLayout)
		mainLayout.addWidget(self.fileListWidget)
		mainLayout.setStretchFactor(ShotLayout,0)
		mainLayout.setStretchFactor(self.fileListWidget,1)

		self.setLayout(mainLayout)


		self.setupUI()
		self.initConnect()

	def initConnect(self):
		self.fileListWidget.itemClicked.connect(self.setThumbnail)

	def setupUI(self):
		self.SequenceLayout.setEnabled(False)

	def setThumbnail(self):
		thumbnailPath = projectExplorer_core.thumbnailPath(self.currentFile)
		if not os.path.exists(thumbnailPath):
			thumbnailPath = self.thumbnailWidget.placeHolder_path

		self.thumbnailWidget.setThumbnail(thumbnailPath)

	def setProject(self, projectName):
		self.fileListWidget.clear()
		self.shotListWidget.clear()

		self.shotListWidget.addItems(core.listShots(projectName))

	def updateFileList(self, projectName):
		self.fileListWidget.clear()

		for version in core.listVersion(projectName, self.currentShot) :
			version_path = projectExplorer_core._replaceData(core.getConfigData("PATH_TEMPLATE"), projectName, self.currentShot)
			item = QListWidgetItem(version)
			item.setData(Qt.UserRole,version_path.replace('${_SCRIPTNAME}', version))

			self.fileListWidget.addItem(item)

	@property
	def currentShot(self):
		return self.shotListWidget.currentItem().text()

	@property
	def currentFile(self):
		return self.fileListWidget.currentItem().data( Qt.UserRole )

def openExplorer(filePath):
	"""Open File explorer after finish."""
	win_publishPath = filePath.replace('/', '\\')
	subprocess.Popen('explorer \/select,\"%s\"' % win_publishPath)

def _nuke_main_window():
	"""Returns Nuke's main window"""
	for obj in QApplication.instance().topLevelWidgets():
		if (obj.inherits('QMainWindow') and
				obj.metaObject().className() == 'Foundry::UI::DockMainWindow'):
			return obj
	else:
		raise RuntimeError('Could not find DockMainWindow instance')

def main ():
	window = ExplorerWindow( parent = _nuke_main_window() )
	window.show()