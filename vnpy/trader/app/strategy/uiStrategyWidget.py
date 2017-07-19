# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''

from vnpy.trader.uiBasicWidget import *
from vnpy.event import Event
from vnpy.trader.vtEvent import *
from PyQt4 import QtGui
from abc import ABCMeta,abstractmethod,abstractproperty


from vnpy.trader.app.strategy.language import text


########################################################################
class ValueMonitor(QtWidgets.QTableWidget):
    """参数监控"""

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super(ValueMonitor, self).__init__(parent)

        self.keyCellDict = {}
        self.cellRowList = []
        self.data = None
        self.inited = False

        self.initUi()

    # ----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setRowCount(1)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(self.NoEditTriggers)
        self.setMaximumHeight(self.sizeHint().height())

    # ----------------------------------------------------------------------
    @abstractmethod
    def updateData(self, list):
        '''更新表格数据'''
        pass


########################################################################
class StrategyManager(QtWidgets.QGroupBox):
    """策略管理组件"""
    signal = QtCore.Signal(type(Event()))

    # ----------------------------------------------------------------------
    def __init__(self,name, parent=None):
        """Constructor"""
        super(StrategyManager, self).__init__(parent)
        self.name = name

        self.initUi()
        # self.updateMonitor()
        # self.registerEvent()

    # ----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setTitle(self.name)
        self.strategyTable = ValueMonitor(self)

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

    # ----------------------------------------------------------------------
    # def updateMonitor(self, event=None):
    #     """显示最新策略列表"""
    #     self.strategyTable.updateData(self.strategyEngine.querySetting())

    # ----------------------------------------------------------------------
    # def registerEvent(self):
    #     """注册事件监听"""
    #     self.signal.connect(self.updateMonitor)
    #     self.eventEngine.register(EVENT_STRATEGY + self.name, self.signal.emit)

    # # ----------------------------------------------------------------------
    # def init(self):
    #     """初始化策略"""
    #     self.ctaEngine.initStrategy(self.name)
    #
    # # ----------------------------------------------------------------------
    # def start(self):
    #     """启动策略"""
    #     self.ctaEngine.startStrategy(self.name)
    #
    # # ----------------------------------------------------------------------
    # def stop(self):
    #     """停止策略"""
    #     self.ctaEngine.stopStrategy(self.name)


########################################################################
class EngineManager(QtWidgets.QWidget):
    """策略引擎管理组件"""
    signal = QtCore.Signal(type(Event()))

    # ----------------------------------------------------------------------
    def __init__(self, strategyEngine, eventEngine, parent=None):
        """Constructor"""
        super(EngineManager, self).__init__(parent)

        self.strategyEngine = strategyEngine
        self.eventEngine = eventEngine
        self.strategyLoaded = False

        self.initUi()
        self.registerEvent()

        # ----------------------------------------------------------------------

    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(text.STRATEGY)

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
        self.strategyManager = StrategyManager()

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

    #-----------------------------------------------------------------------
    def load(self):
        self.strategyEngine.loadStrategy(self.strategyEngine.querySetting())
        self.initStrategyManager()
        self.strategyLoaded = True
        self.strategyEngine.writeLog(text.STRATEGY_LOADED)

    # ----------------------------------------------------------------------
    def initStrategyManager(self):
        """初始化策略管理组件界面"""
        w = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()

        strategyManager = StrategyManager(self.strategyEngine, self.eventEngine, text.STRATEGY_LIST)
        vbox.addWidget(strategyManager)

        vbox.addStretch()

        w.setLayout(vbox)
        self.scrollArea.setWidget(w)

        # ----------------------------------------------------------------------

    # def initAll(self):
    #     """全部初始化"""
    #     for name in self.ctaEngine.strategyDict.keys():
    #         self.ctaEngine.initStrategy(name)
    #
    #         # ----------------------------------------------------------------------
    #
    # def startAll(self):
    #     """全部启动"""
    #     for name in self.ctaEngine.strategyDict.keys():
    #         self.ctaEngine.startStrategy(name)
    #
    # # ----------------------------------------------------------------------
    # def stopAll(self):
    #     """全部停止"""
    #     for name in self.ctaEngine.strategyDict.keys():
    #         self.ctaEngine.stopStrategy(name)



    def updateLog(self, event):
        """更新相关日志"""
        log = event.dict_['data']
        content = '\t'.join([log.logTime, log.logContent])
        self.logMonitor.append(content)

    # ----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        pass
        #self.signal.connect(self.updateaLog)
        #self.eventEngine.register(EVENT_LOG, self.signal.emit)

    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtWidgets.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                               text.SAVE_POSITION_QUESTION, QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.engine.savePosition()

        event.accept()










