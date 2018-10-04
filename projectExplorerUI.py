import time
import os
import sys
import subprocess
import shutil

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

__VERISON__ = "1.2"
# V1.0 All main functions working
# V1.1 Fix Wrong configure path
# V1.2 Support shot's sub-folder

class PreferenceWindow(QDialog) :

	def __init__(self, parent = None):
		super (PreferenceWindow, self).__init__(parent)

		mainLayout = QGridLayout()

		formLayout = QFormLayout()
		self.rootPath_input = QLineEdit(self)
		self.rootPath_input.setText(core.configData['EXT_VAR']['ROOT'])
		formLayout.addRow("Root path:", self.rootPath_input)
		
		self.submitbtn = QPushButton(self)
		self.submitbtn.setText("Save")
		mainLayout.addLayout( formLayout,0,0, columnSpan = 3)
		mainLayout.addWidget(self.submitbtn, 1,0)		
		self.setLayout(mainLayout)

		self.submitbtn.clicked.connect(self.submit_onClicked)

	def submit_onClicked(self, *args):
		projectExplorer_core.updatePref(data = {"ROOT":self.rootPath_input.text()})
		self.close()

class ExplorerWindow(QMainWindow):

	setting = settings = QSettings( "Shape and Light", "Nuke Explorer")

	def __init__(self, parent = None):
		super(ExplorerWindow, self).__init__(parent)
		self.InitUI()
		self.setupUI()
		self.initConnect()

	def InitUI(self):
		
		self.setWindowTitle("Nuke project explorer V%s"%__VERISON__)

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
		mainLayout.setContentsMargins(5,5,5,5)
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
		# Restore Data
		self.settings.beginGroup("MainWindow")
		self.restoreGeometry(self.settings.value("geometry"))
		self.restoreState(self.settings.value("state"))
		self.settings.endGroup()

		prev_project = self.settings.value("projectData/project")
		prev_shot = self.settings.value("projectData/shot")
		print prev_project

		# Setup
		# Set previous project
		projectList = core.listProjects()
		self.headWidget.projectComboBox.addItems(projectList)
		if prev_project in projectList :
			index = self.headWidget.projectComboBox.findText(prev_project, Qt.MatchExactly)
			self.headWidget.projectComboBox.setCurrentIndex(index)

		# Set file current project
		self.fileWidget.setProject(self.currentProject)

		# Set previous shot
		if self.fileWidget.shotListWidget.findItems(prev_shot, Qt.MatchExactly):
			shotItem = self.fileWidget.shotListWidget.findItems(prev_shot, Qt.MatchExactly)
			self.fileWidget.shotListWidget.setCurrentItem(shotItem[0])
			self.fileWidget.updateFileList()

	def initConnect(self):
		self.headWidget.projectComboBox.activated.connect(lambda : self.fileWidget.setProject(self.currentProject))
		self.saveButton.clicked.connect(self.save_OnClicked)
		self.openButton.clicked.connect(self.open_onClicked)
		self.fileWidget.shotListWidget.itemClicked.connect(self.fileWidget.updateFileList)
		self.fileWidget.fileListWidget.itemDoubleClicked.connect(self.open_onClicked)

	def closeEvent(self, event):
		print "Saving current state data ..."

		self.settings.beginGroup("MainWindow")
		self.settings.setValue("geometry", self.saveGeometry())
		self.settings.setValue("state", self.saveState())
		self.settings.endGroup()

		self.settings.beginGroup("projectData")
		self.settings.setValue("project",  self.currentProject)
		self.settings.setValue("shot", self.fileWidget.currentShot)
		self.settings.endGroup()

	def save_OnClicked(self):
		savePath = core.saveIncrement(self.currentProject, self.fileWidget.currentShot)

		projectExplorer_core.saveFrame(thumbnailPath = projectExplorer_core.thumbnailPath(savePath))
		self.fileWidget.updateFileList()

	def open_onClicked(self):
		print self.fileWidget.currentFile
		core.openScript(self.fileWidget.currentFile)

	def callPrefWindow(self):
		prefWin = PreferenceWindow(parent = self)
		prefWin.exec_()

	def callDocumentLink(self):
		print "callDocumentLink"
		QDesktopServices.openUrl(QUrl('https://github.com/Shayen/SAL-Nuke-ProjectExplorer'))

	def callGithubLink(self):
		print "callGithubLink"
		QDesktopServices.openUrl(QUrl('https://github.com/Shayen/SAL-Nuke-ProjectExplorer'))

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
			imagepath = self.placeHolder_path

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
		self.projectSetting = QPushButton(self)
		self.projectSetting.setIcon(QIcon(currentDir + "/image/setting.png"))
		verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

		self.projectLayout.addWidget(self.projectLabel)
		self.projectLayout.addWidget(self.projectComboBox)
		self.projectLayout.addWidget(self.projectSetting)
		self.projectLayout.addItem(verticalSpacer)
		self.projectLayout.setStretch(3,1)

		mainLayout.addWidget(self.title)
		mainLayout.addLayout(self.projectLayout)

		self.setLayout(mainLayout)

class fileWidget(QWidget):

	project = ''

	def __init__(self, parent= None):
		super(fileWidget, self).__init__(parent)
		
		mainLayout = QHBoxLayout()
		ShotLayout = QVBoxLayout()

		self.thumbnailWidget = thumbnailWidget(self)

		self.shotListWidget = QListWidget(self)
		self.shotLabelLayout = QHBoxLayout()
		self.addShotButton = QPushButton("+",self)
		self.addShotButton.setMaximumWidth(20)
		verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.shotLabelLayout.addWidget(QLabel(self.tr("Shot : ")))
		self.shotLabelLayout.addItem(verticalSpacer)
		self.shotLabelLayout.addWidget(self.addShotButton)
		self.shotLabelLayout.setStretch(1,1)

		ShotLayout.addWidget(self.thumbnailWidget)
		ShotLayout.addLayout(self.shotLabelLayout)
		ShotLayout.addWidget(self.shotListWidget)
		ShotLayout.setStretch(3,1)

		self.fileListWidget = QListWidget(self)
		self.fileListWidget.setContextMenuPolicy(Qt.CustomContextMenu)

		mainLayout.addLayout(ShotLayout)
		mainLayout.addWidget(self.fileListWidget)
		mainLayout.setStretchFactor(ShotLayout,0)
		mainLayout.setStretchFactor(self.fileListWidget,1)

		self.setLayout(mainLayout)


		self.setupUI()
		self.initConnect()

	def initConnect(self):
		self.fileListWidget.itemClicked.connect(self.setThumbnail)
		self.addShotButton.clicked.connect(self.addShot)

		# Add right click menu
		self.fileListWidget.connect(
			self.fileListWidget, SIGNAL("customContextMenuRequested(QPoint)"),
			self.fileListWidgetItemRightClicked)

	def setupUI(self):
		pass

	def setThumbnail(self):
		thumbnailPath = projectExplorer_core.thumbnailPath(self.currentFile)
		if not os.path.exists(thumbnailPath):
			thumbnailPath = self.thumbnailWidget.placeHolder_path

		self.thumbnailWidget.setThumbnail(thumbnailPath)

	def setProject(self, projectName):
		self.project = projectName
		self.fileListWidget.clear()
		self.shotListWidget.clear()

		self.shotListWidget.addItems(core.listShots(self.project))

	def updateFileList(self):
		self.fileListWidget.clear()

		for version in core.listVersion(self.project, self.currentShot) :
			version_path = projectExplorer_core._replaceData(core.getConfigData("PATH_TEMPLATE"), self.project, self.currentShot)

			item = QListWidgetItem(self.fileListWidget)
			if version.endswith(".nk"):
				item.setIcon(QIcon(currentDir + "/image/NukeDoc16.png"))
			widgetitem = fileListItem(version)
			widgetitem.setData(version_path.replace('${_SCRIPTNAME}', version))
			item.setSizeHint(widgetitem.sizeHint())

			# self.fileListWidget.addItem(item)
			self.fileListWidget.addItem(item)
			self.fileListWidget.setItemWidget(item, widgetitem)

	def addShot(self):

		path = projectExplorer_core._replaceData(core.getConfigData("PATH_TEMPLATE").split('/${_SHOTSNAME}/')[0],
												 project = self.project)
		is_folderExists = True
		while is_folderExists:
			shotname, ok = QInputDialog.getText(self, "Create new shot", "Shot name:")

			if ok:
				is_folderExists = shotname in os.listdir(path)
			else:
				return

		folderPath = "%s/%s"%(path, shotname)
		os.mkdir(folderPath)

		# Refresh shot-list
		self.setProject(self.project)

	def __renameScript(self, filepath):

		oldname = os.path.basename(filepath)
		dirname = os.path.dirname(filepath)

		is_folderExists = True
		while is_folderExists:
			newname, ok = QInputDialog.getText(self, "Rename", "new name:",  QLineEdit.Normal, oldname)

			if ok:
				is_folderExists = newname in os.listdir(dirname)
			else:
				return

		newPath = "%s/%s"%(dirname, newname)
		os.rename(filepath, newPath)

		self.updateFileList()

	def __duplicateScript(self, filepath):

		def getLastVersion(dirname, basename):
			count = 0
			for filename in os.listdir(dirname):
				if filename.startswith(basename):
					count += 1

			if count > 0 :
				return (count + 1)
			else :
				return  1

		dirname = os.path.dirname(filepath)
		basename, ext = os.path.splitext(os.path.basename(filepath))

		if '_copy' in basename:
			basename = basename.split("_copy")[0]

		increment_number = getLastVersion(dirname, basename)
		newname = basename + '_copy' + str(increment_number) + ext
		while newname in os.listdir(dirname):
			increment_number += 1
			newname = basename + '_copy' + str(increment_number) + ext

		newpath = '%s/%s'%(dirname, newname)
		shutil.copy2(filepath, newpath)

		self.updateFileList()

	def fileListWidgetItemRightClicked(self, QPos):

		self.listMenu = QMenu()
		menu_copyNameItem = self.listMenu.addAction("Copy name")
		menu_copyPathItem = self.listMenu.addAction("Copy path")
		self.listMenu.addSeparator()
		menu_rename = self.listMenu.addAction("Rename")
		menu_duplicate = self.listMenu.addAction("Duplicate")
		self.listMenu.addSeparator()
		menu_updatethumbnail = self.listMenu.addAction("Update Thumbnail")
		menu_openExplorer = self.listMenu.addAction("Open Containing Folder ...")

		menu_openExplorer.triggered.connect(lambda : openExplorer(os.path.dirname(self.currentFile)))
		menu_copyNameItem.triggered.connect(lambda : copyTextToClipboard(os.path.basename(self.currentFile)))
		menu_copyPathItem.triggered.connect(lambda : copyTextToClipboard(self.currentFile))
		menu_rename.triggered.connect(lambda : self.__renameScript(self.currentFile))
		menu_updatethumbnail.triggered.connect(self.__menu_updatethumbnail_onCLicked)
		menu_duplicate.triggered.connect(lambda : self.__duplicateScript(self.currentFile))

		parentPosition = self.fileListWidget.mapToGlobal(QPos)
		self.listMenu.exec_(parentPosition)

	def __menu_updatethumbnail_onCLicked(self):
		msgBox = QMessageBox().question(self, "Confirm Dialog", "Do you want to update thumbnail?",
										QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

		if msgBox == QMessageBox.Ok:
			projectExplorer_core.saveFrame(thumbnailPath=projectExplorer_core.thumbnailPath(self.currentFile))
		else:
			return
		self.setThumbnail()

	@property
	def currentShot(self):
		if not self.shotListWidget.currentItem():
			return None

		return self.shotListWidget.currentItem().text()

	@property
	def currentFile(self):
		if not self.fileListWidget.currentItem():
			return None

		return self.fileListWidget.itemWidget(self.fileListWidget.currentItem()).data

class fileListItem(QWidget):

	def __init__(self, text = '', parent = None):
		super(fileListItem, self).__init__(parent)

		mainLayout = QHBoxLayout()
		self.itemname = QLabel(self)
		verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.itemModified = QLabel(self)

		mainLayout.addWidget(self.itemname)
		mainLayout.addItem(verticalSpacer)
		mainLayout.addWidget(self.itemModified)
		mainLayout.setStretch(1,1)
		mainLayout.setContentsMargins(1,6,10,6)
		self.setLayout(mainLayout)

		self.setText(text)
		self.setStyleSheet("font-size: 10pt;")

	def setText(self, text):
		self.itemname.setText(text)

	def setData(self, data):
		self.data = data

		mtime = time.strftime('%m/%d/%Y %H:%M:%S',time.localtime(os.path.getmtime(data)))
		self.itemModified.setText(mtime)

	def text(self):
		return self.itemname.text()

def copyTextToClipboard(text):
	clipBoard = QApplication.clipboard()
	clipBoard.setText(text)

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