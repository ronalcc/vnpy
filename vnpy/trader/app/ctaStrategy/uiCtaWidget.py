# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''

from vnpy.trader.uiBasicWidget import *
from vnpy.event import Event
from vnpy.trader.vtEvent import *
from PyQt4 import QtGui
from vnpy.trader.app.strategy.uiStrategyWidget import *

from vnpy.trader.app.ctaStrategy.language import text


########################################################################
class CtaValueMonitor(ValueMonitor):
    """表格"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super(CtaValueMonitor, self).__init__(parent)
        
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        super(ValueMonitor,self).initUi()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            [text.CTA_STRATEGYNAME, text.CTA_STRATEGYTYPE, text.CTA_COMMENT, text.CTA_AUTHOR, text.CTA_OPER])
        self.horizontalHeader().resizeSection(0,200)
        self.horizontalHeader().resizeSection(1,100)
        self.horizontalHeader().resizeSection(2,500)
        self.horizontalHeader().resizeSection(3,100)
        self.horizontalHeader().resizeSection(4,300)

        self.setColumnWidth(0,200)
        self.setColumnWidth(1,100)
        self.setColumnWidth(2,500)
        self.setColumnWidth(3,100)
        self.setColumnWidth(4,300)
    #----------------------------------------------------------------------
    def updateData(self, list):
        self.setRowCount(len(list))
        if not self.inited:

            row = 0
            while(row<len(list)):
               data = list[row]
               self.setItem(row,0,QtGui.QTableWidgetItem(unicode(data['strategyName'])))
               self.setItem(row, 1, QtGui.QTableWidgetItem(unicode(data['strategyType'])))
               self.setItem(row, 2, QtGui.QTableWidgetItem(unicode(data['comment'])))
               self.setItem(row, 3, QtGui.QTableWidgetItem(unicode(data['author'])))
               row +=1
            self.inited = True
        else:
            row = 0
            while(row<len(list)):
              data = list[row]
              self.item(row,0).setText(unicode(data['strategyName']))
              self.item(row,1).setText(unicode(data['strategyType']))
              self.item(row, 2).setText(unicode(data['comment']))
              self.item(row, 3).setText(unicode(data['author']))


########################################################################
class CtaStrategyManager(StrategyManager):
    """策略管理组件"""
    signal = QtCore.Signal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, name, parent=None):
        """Constructor"""
        super(CtaStrategyManager, self).__init__(ctaEngine, eventEngine, name,parent)

    
    #----------------------------------------------------------------------
    def init(self):
        """初始化策略"""
        self.ctaEngine.initStrategy(self.name)
    
    #----------------------------------------------------------------------
    def start(self):
        """启动策略"""
        self.ctaEngine.startStrategy(self.name)
        
    #----------------------------------------------------------------------
    def stop(self):
        """停止策略"""
        self.ctaEngine.stopStrategy(self.name)


########################################################################
class CtaEngineManager(EngineManager):
    """CTA引擎管理组件"""

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, parent=None):
        """Constructor"""
        super(CtaEngineManager, self).__init__(ctaEngine, eventEngine,parent)
        self.resize(1200,900)

        
    #----------------------------------------------------------------------
    def initAll(self):
        """全部初始化"""
        for name in self.ctaEngine.strategyDict.keys():
            self.ctaEngine.initStrategy(name)    
            
    #----------------------------------------------------------------------
    def startAll(self):
        """全部启动"""
        for name in self.ctaEngine.strategyDict.keys():
            self.ctaEngine.startStrategy(name)
            
    #----------------------------------------------------------------------
    def stopAll(self):
        """全部停止"""
        for name in self.ctaEngine.strategyDict.keys():
            self.ctaEngine.stopStrategy(name)
            
    #----------------------------------------------------------------------
    def load(self):
            self.ctaEngine.loadStrategy(self.ctaEngine.querySetting())
            self.initStrategyManager()
            self.strategyLoaded = True
            self.ctaEngine.writeCtaLog(text.STRATEGY_LOADED)
        

        
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtWidgets.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                           text.SAVE_POSITION_QUESTION, QtWidgets.QMessageBox.Yes | 
                                           QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    
        if reply == QtWidgets.QMessageBox.Yes: 
            self.ctaEngine.savePosition()
            
        event.accept()
        
        
    
    
    
    



    
    