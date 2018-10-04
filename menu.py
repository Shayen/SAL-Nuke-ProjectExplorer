import nuke


def runNukeExplorer():
	import nukeExplorer.projectExplorerUI as ui
	reload(ui)

	ui.main()


nuke.menu('Nuke').addCommand('SAL Tools/File manager', "runNukeExplorer()", 'ctrl+shift+o')