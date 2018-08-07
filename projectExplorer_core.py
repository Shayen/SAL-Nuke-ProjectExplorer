import os
import re
import errno
import json
import shutil

import nuke

# from source import lucidity

currentDir = os.path.dirname(__file__).replace("\\", '/')
configPath = "H:/programming/Python/nukeProjectExplorer/configure.conf"

def read_configFile(file_path):

	with open(file_path, "r") as f :
		json_string = f.read()
	f.close()

	try:
		# Remove commens from JSON (makes sample config options easier)
		regex = r'\s*(#|\/{2}).*$'
		regex_inline = r'(:?(?:\s)*([A-Za-z\d\.{}]*)|((?<=\").*\"),?)(?:\s)*(((#|(\/{2})).*)|)$'
		lines = json_string.split('\n')

		for index, line in enumerate(lines):
			if re.search(regex, line):
				if re.search(r'^' + regex, line, re.IGNORECASE):
					lines[index] = ""
				elif re.search(regex_inline, line):
					lines[index] = re.sub(regex_inline, r'\1', line)

		data = json.loads('\n'.join(lines))

	except ValueError as e:
		raise IOError(file_path)

	except Exception as e:
		raise e

	return data


class ExplorerCore(object):

	def __init__(self):
		super(ExplorerCore, self).__init__()
		self.configData = read_configFile(configPath)

	def getConfigData(self, *args):
		data = eval("self.configData" + "".join(["[\"" + key + "\"]" for key in args]))
		
		pattern = re.compile("(?<=\${)([A-Za-z0-9]*)(?=})")
		match = pattern.findall(data)

		if match:
			for key in match :
				if key in self.configData['EXT_VAR'].keys():
					data = data.replace("${" + key + "}", self.configData['EXT_VAR'][key])

		return data

	def listProjects(self):
		projectPath = self.getConfigData('PATH_TEMPLATE').split("${_PROJECTSNAME}")[0]
		nuke.tprint("PROJECTS : %s"%projectPath)

		if not os.path.exists(projectPath) :
			nuke.tprint("ERROR : Path not found \"%s\""%projectPath)
			return []

		return [item for item in os.listdir(projectPath) if os.path.isdir(projectPath)]

	def listShots(self,projectname):
		shotPath = self.getConfigData('PATH_TEMPLATE').split("${_SHOTSNAME}")[0]
		shotPath = shotPath.replace("${_PROJECTSNAME}", projectname)

		if not os.path.exists(shotPath) :
			nuke.tprint("ERROR : Path not found \"%s\""%shotPath)
			return []

		return [item for item in os.listdir(shotPath) if os.path.isdir(shotPath)]

	def listVersion(self, project, shot):
		savePath = _replaceData(self.getConfigData("PATH_TEMPLATE"), project, shot)
		shotDirPath = os.path.dirname(savePath)

		return [f for f in os.listdir(shotDirPath) if os.path.isfile(shotDirPath + '/' + f) and f.endswith(('nk', 'nknc'))]

	def openScript(self,scriptPath):
		nuke.tprint("Openning... \"{}\"".format(scriptPath))
		nuke.scriptOpen(scriptPath)

	def saveIncrement(self, project, shot):

		if not project or not shot :
			nuke.tprint("Please select shot")
			return False

		savePath = _replaceData(self.getConfigData("PATH_TEMPLATE"), project, shot)
		filename = _replaceData(self.getConfigData("SCRIPTNAME_TEMPLATE"), project, shot, get_lastversion(savePath))
		savePath = savePath.replace("${_SCRIPTNAME}", filename)

		nuke.scriptSaveAs(savePath)
		nuke.tprint("Save file : %s" %(savePath))
		return savePath

def get_lastversion(shotPath):

	shotDirPath = os.path.dirname(shotPath)

	version = []
	versionedFiles = [f for f in os.listdir(shotDirPath) if os.path.isfile(shotDirPath + '/' + f) and f.endswith(('nk', 'nknc'))]

	if versionedFiles :
		for file in versionedFiles :

			pattern = re.compile("([vV][0-9]{3}|[vV][0-9]{4})")
			match = pattern.findall(file)

			if match :
				version.append(int(match[0][1:]))

	else :
		return 1

	return max(version) + 1

def _replaceData( data ,project, shot, version= ''):

	'''
	_PROJECTSCODE
	_SHOTSNAME
	_VERSION
	_EXTENSION
	'''

	_mapping = {	"${_PROJECTSNAME}"	: project,
					"${_PROJECTSCODE}"  : "test",
					"${_SHOTSNAME}"		: shot,
					"${_VERSION}"		: "%03d"%(version or 0),
					"${_EXTENSION}"		: "nk" }

	for key,value in _mapping.items():
		data = data.replace(key, value)

	return data

def thumbnailPath(filePath):
	thumbnailPath = os.path.dirname(filePath)
	thumbnailPath += '/thumbnails/' + os.path.splitext(os.path.basename(filePath))[0] + '.png'

	return thumbnailPath

def saveFrame(thumbnailPath):
	viewer 		= nuke.activeViewer()
	inputNode 	= nuke.ViewerWindow.activeInput(viewer)
	viewNode 	= nuke.activeViewer().node()
	filetype 	= 'png'

	try:

		if inputNode != None:
			selInput = nuke.Node.input(viewNode, inputNode)
			
			if thumbnailPath != None:

				if not os.path.exists(os.path.dirname(thumbnailPath)):
					os.makedirs( os.path.dirname(thumbnailPath) )
				
				input_w = selInput.width()
				input_h = selInput.height()
				factor  = input_h / 448

				w = int(input_w / factor)
				h = int(input_h / factor)

				reformat= nuke.nodes.Reformat(format="%s %s" % (w, h), resize="width")
				reformat.setInput(0,selInput)
				write = nuke.nodes.Write(file = thumbnailPath, name = 'WriteSaveThisFrame', file_type=filetype)
				write.setInput(0,reformat)

				curFrame = int(nuke.knob("frame"))
				nuke.execute(write.name(), curFrame, curFrame)

				# Clear
				nuke.delete(write)
				nuke.delete(reformat)

				# Succcess
				# nuke.tprint("Save thumbnail : " + thumbnailPath)
				return thumbnailPath
		else:
			nuke.message("This viewer don't have any input connected!")

	except Exception as e:
		nuke.tprint(str(e))

if __name__ == '__main__':
	print listProjects()