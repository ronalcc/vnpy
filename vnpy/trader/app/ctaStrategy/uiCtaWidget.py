# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''

from vnpy.trader.uiBasicWidget import *
from vnpy.event import Event
from vnpy.trader.vtEvent import *
from PyQt4 import QtGui


from vnpy.trader.app.ctaStrategy.language import text


########################################################################
class CtaValueMonitor(QtWidgets.QTableWidget):
    """参数监控"""

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
       # self.setRowCount(1)
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
class CtaStrategyManager(QtWidgets.QGroupBox):
    """策略管理组件"""
    signal = QtCore.Signal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, name, parent=None):
        """Constructor"""
        super(CtaStrategyManager, self).__init__(parent)
        
        self.ctaEngine = ctaEngine
        self.eventEngine = eventEngine
        self.name = name
        
        self.initUi()
        self.updateMonitor()
        self.registerEvent()
        
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
    def updateMonitor(self, event=None):
        """显示最新策略列表"""
        self.strategyTable.updateData(self.ctaEngine.querySetting())
            
    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.signal.connect(self.updateMonitor)
        self.eventEngine.register(EVENT_CTA_STRATEGY+self.name, self.signal.emit)
    
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
class CtaEngineManager(QtWidgets.QWidget):
    """CTA引擎管理组件"""
    signal = QtCore.Signal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, parent=None):
        """Constructor"""
        super(CtaEngineManager, self).__init__(parent)
        
        self.ctaEngine = ctaEngine
        self.eventEngine = eventEngine
        
        self.strategyLoaded = False
        
        self.initUi()
        self.registerEvent()
        self.resize(1200,900)
        # 记录日志
        self.ctaEngine.writeCtaLog(text.CTA_ENGINE_STARTED)        
        
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(text.CTA_STRATEGY)
        
        # 按钮
        loadButton = QtWidgets.QPushButton(text.LOAD_STRATEGY)
        initAllButton = QtWidgets.QPushButton(text.INIT_ALL)
        startAllButton = QtWidgets.QPushButton(text.START_ALL)
        stopAllButton = QtWidgets.QPushButton(text.STOP_ALL)
        savePositionButton = QtWidgets.QPushButton(text.SAVE_POSITION_DATA)
        
        loadButton.clicked.connect(self.load)
        initAllButton.clicked.connect(self.initAll)
        startAllButton.clicked.connect(self.startAll)
        stopAllButton.clicked.connect(self.stopAll)
        savePositionButton.clicked.connect(self.ctaEngine.savePosition)
        
        # 滚动区域，放置所有的CtaStrategyManager
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        
        # CTA组件的日志监控
        self.ctaLogMonitor = QtWidgets.QTextEdit()
        self.ctaLogMonitor.setReadOnly(True)
        self.ctaLogMonitor.setMaximumHeight(200)
        
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
        vbox.addWidget(self.ctaLogMonitor)
        self.setLayout(vbox)
        self.load()
    #----------------------------------------------------------------------
    def initStrategyManager(self):
        """初始化策略管理组件界面"""        
        w = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()
        
        strategyManager = CtaStrategyManager(self.ctaEngine, self.eventEngine, text.CTA_LIST)
        vbox.addWidget(strategyManager)
        
        vbox.addStretch()
        
        w.setLayout(vbox)
        self.scrollArea.setWidget(w)   
        
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
    def updateCtaLog(self, event):
        """更新CTA相关日志"""
        log = event.dict_['data']
        content = '\t'.join([log.logTime, log.logContent])
        self.ctaLogMonitor.append(content)
    
    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.signal.connect(self.updateCtaLog)
        self.eventEngine.register(EVENT_CTA_LOG, self.signal.emit)
        
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtWidgets.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                           text.SAVE_POSITION_QUESTION, QtWidgets.QMessageBox.Yes | 
                                           QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    
        if reply == QtWidgets.QMessageBox.Yes: 
            self.ctaEngine.savePosition()
            
        event.accept()
        
        
    
    
    
    



    
    