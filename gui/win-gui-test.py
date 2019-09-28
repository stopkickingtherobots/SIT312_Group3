# coding: utf-8
# Reference: https://gist.github.com/sergeyfarin/c689fd0171f95865055fad857579bc94

import sys
import os
# import site
# site.addsitedir('/usr/local/lib/python2.7/site-packages')
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

app = QtWidgets.QApplication(sys.argv)
view = QtWebEngineWidgets.QWebEngineView()

view.load(QtCore.QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]+r'\html\tracking_realtime.html'))

view.show()
sys.exit(app.exec_())