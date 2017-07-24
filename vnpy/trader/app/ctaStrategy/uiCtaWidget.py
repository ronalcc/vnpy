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
from vnpy.trader.language import text as gtext

########################################################################
class CtaValueMonitor(QtWidgets.QTableWidget):
    """表格"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super(CtaValueMonitor, self).__init__(parent)

        self.keyCellDict = {}
        self.cellRowList = []
        self.data = None
        self.inited = False

        self.initUi()
        
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setRowCount(1)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(self.NoEditTriggers)
        self.setMaximumHeight(self.sizeHint().height())
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
               buttonInstanceManage = QtWidgets.QPushButton(gtext.INSTANCEMANAGE)
               self.setItem(row,0,QtGui.QTableWidgetItem(unicode(data['strategyName'])))
               self.setItem(row, 1, QtGui.QTableWidgetItem(unicode(data['strategyType'])))
               self.setItem(row, 2, QtGui.QTableWidgetItem(unicode(data['comment'])))
               self.setItem(row, 3, QtGui.QTableWidgetItem(unicode(data['author'])))
               self.setItem(row,4,QtGui.QTableWidgetItem(buttonInstanceManage))
               row +=1
            self.inited = True
        else:
            row = 0
            while(row<len(list)):
              data = list[row]
              buttonInstanceManage = QtWidgets.QPushButton(gtext.INSTANCEMANAGE)
              self.item(row,0).setText(unicode(data['strategyName']))
              self.item(row,1).setText(unicode(data['strategyType']))
              self.item(row, 2).setText(unicode(data['comment']))
              self.item(row, 3).setText(unicode(data['author']))
              self.setItem(row, 4, QtGui.QTableWidgetItem(buttonInstanceManage))


########################################################################
class CtaStrategyManager(QtWidgets.QGroupBox):
    """策略管理组件"""
    signal = QtCore.Signal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, name, parent=None):
       """Constructor"""
       super(CtaStrategyManager, self).__init__(parent)
       self.name = name
       self.initUi()

    
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setTitle(self.name)
        self.strategyTable = CtaValueMonitor(self)


        # self.paramMonitor = CtaValueMonitor(self)
        # self.varMonitor = CtaValueMonitor(self)
        #
        # height = 65
        # self.paramMonitor.setFixedHeight(height)
        # self.varMonitor.setFixedHeight(height)
        #
        # buttonInit = QtWidgets.QPushButton(text.INIT)
        # buttonStart = QtWidgets.QPushButton(text.START)
        # buttonStop = QtWidgets.QPushButton(text.STOP)
        # buttonInit.clicked.connect(self.init)
        # buttonStart.clicked.connect(self.start)
        # buttonStop.clicked.connect(self.stop)
        #
        # hbox1 = QtWidgets.QHBoxLayout()
        # hbox1.addWidget(buttonInit)
        # hbox1.addWidget(buttonStart)
        # hbox1.addWidget(buttonStop)
        # hbox1.addStretch()
        #
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.strategyTable)
        #
        # hbox3 = QtWidgets.QHBoxLayout()
        # hbox3.addWidget(self.varMonitor)
        #
        vbox = QtWidgets.QVBoxLayout()
        # vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        # vbox.addLayout(hbox3)
        #
        self.setLayout(vbox)


    
    #----------------------------------------------------------------------
    def start(self):
        """启动策略"""
        self.ctaEngine.startStrategy(self.name)
        
    #----------------------------------------------------------------------
    def stop(self):
        """停止策略"""
        self.ctaEngine.stopStrategy(self.name)




########################################################################
class CtaEngineManager(QtWidgets.QWidget):
    """CTA引擎管理组件"""

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine,strategyType, parent=None):
        """Constructor"""
        super(CtaEngineManager, self).__init__(parent)
        self.strategyEngine = ctaEngine
        self.eventEngine = eventEngine
        self.strategyLoaded = False
        self.strategyType = strategyType
        self.initUi()
        self.updateMonitor(strategyType)
        self.resize(1200,900)


    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(gtext.STRATEGY)

        # 按钮
        # loadButton = QtWidgets.QPushButton(text.LOAD_STRATEGY)
        # initAllButton = QtWidgets.QPushButton(text.INIT_ALL)
        # startAllButton = QtWidgets.QPushButton(text.START_ALL)
        # stopAllButton = QtWidgets.QPushButton(text.STOP_ALL)
        # savePositionButton = QtWidgets.QPushButton(text.SAVE_POSITION_DATA)

        # loadButton.clicked.connect(self.load)
        # initAllButton.clicked.connect(self.initAll)
        # startAllButton.clicked.connect(self.startAll)
        # stopAllButton.clicked.connect(self.stopAll)
        # savePositionButton.clicked.connect(self.ctaEngine.savePosition)

        # 滚动区域，放置strategyManager
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.strategyManager = CtaStrategyManager(self.strategyType)
        # w = QtGui.QWidget()
        # vbox = QtGui.QVBoxLayout()
        # vbox.addWidget(self.strategyTable)
        # vbox.addStretch()
        # w.setLayout(vbox)
        self.scrollArea.setWidget( self.strategyManager)
        # 组件的日志监控
        self.logMonitor = QtWidgets.QTextEdit()
        self.logMonitor.setReadOnly(True)
        self.logMonitor.setMaximumHeight(200)

        # 设置布局
        # hbox2 = QtWidgets.QHBoxLayout()
        # hbox2.addWidget(loadButton)
        # hbox2.addWidget(initAllButton)
        # hbox2.addWidget(startAllButton)
        # hbox2.addWidget(stopAllButton)
        # hbox2.addWidget(savePositionButton)
        # hbox2.addStretch()
        #
        vbox = QtWidgets.QVBoxLayout()
        # vbox.addLayout(hbox2)
        vbox.addWidget(self.scrollArea)
        vbox.addWidget(self.logMonitor)
        self.setLayout(vbox)
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
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtWidgets.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                           text.SAVE_POSITION_QUESTION, QtWidgets.QMessageBox.Yes | 
                                           QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    
        if reply == QtWidgets.QMessageBox.Yes: 
            self.ctaEngine.savePosition()
            
        event.accept()
        
        
    #----------------------------------------------------------------------
    def updateMonitor(self,strategyType):
        """更新查询结果集"""
        list = self.strategyEngine.mainEngine.dbQuery("strategy", "strategyClass", {"strategyType": strategyType})
        if len(list)>0:
          self.strategyManager.strategyTable.updateData(list)
    
    
    



    
    