# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\py\chenPy\doc\QT\INSTANCE\form.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from vnpy.trader.uiBasicWidget import *



class uiStrategyInstanceMain(QtWidgets.QWidget):


       def __init__(self,strategyEngine, eventEngine,strategyInstanceName, parent=None):
             self.strategyEngine = strategyEngine
             self.eventEngine = eventEngine
             self.name = strategyInstanceName
             self.initUi()

       def initUi(self):
           self.setWindowTitle(self.name)




class uiStrategyInstanceList(QtWidgets.QTableWidget):

      def __init__(self):
          pass
