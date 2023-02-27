from qtpy import QtGui


class DataStatus:

	ready = "Ready"
	in_progress = "In progress ..."
	failed = "Failed!"
	in_queue = "In queue"
	done = "Done"


class ColorDataStatus:

	ready = 'green'
	ready_button = 'light green'
	in_progress = 'grey'
	failed = 'red'
	in_queue = 'cyan'


READY = QtGui.QColor(0, 255, 0)
IN_PROGRESS = QtGui.QColor(155, 155, 155)
FAILED = QtGui.QColor(255, 0, 0)
IN_QUEUE = QtGui.QColor(0, 255, 255)


