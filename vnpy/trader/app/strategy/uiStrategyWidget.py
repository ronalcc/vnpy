# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''

from vnpy.trader.uiBasicWidget import *
from vnpy.event import Event
from vnpy.trader.vtEvent import *
from PyQt4 import QtGui
from abc import ABCMeta,abstractmethod,abstractproperty
from vnpy.trader.language import text as gtext


from vnpy.trader.app.strategy.language import text


########################################################################
class strategyInstanceTable(QtWidgets.QTableWidget):
    """表格"""

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super(strategyInstanceTable, self).__init__(parent)

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
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            [text.CTA_STRATEGYNAME, text.CTA_STRATEGYTYPE, text.CTA_COMMENT, text.CTA_AUTHOR, text.CTA_OPER])

    # ----------------------------------------------------------------------
    def updateData(self, list):
        self.setRowCount(len(list))
        # if not self.inited:

        row = 0
        while (row < len(list)):
            data = list[row]
            buttonInstanceManage = QtWidgets.QPushButton(gtext.INSTANCEMANAGE)
            buttonInstanceManage.clicked.connect(lambda: self.openStrategy(data['strategyClass']))
            self.setItem(row, 0, QtGui.QTableWidgetItem(unicode(data['strategyClass'])))
            self.setItem(row, 1, QtGui.QTableWidgetItem(unicode(data['strategyType'])))
            self.setItem(row, 2, QtGui.QTableWidgetItem(unicode(data['comment'])))
            self.setItem(row, 3, QtGui.QTableWidgetItem(unicode(data['author'])))
            self.setCellWidget(row, 4, buttonInstanceManage)
            row += 1
        self.inited = True

    # -----------------------------------------------------------------------------------------
    def openStrategy(self, strategyInstanceId):
        pass


########################################################################
class StrategyMain(QtWidgets.QWidget):

    # ----------------------------------------------------------------------
    def __init__(self, strategyEngine, eventEngine, strategyType, parent=None):
            """Constructor"""
            super(StrategyMain, self).__init__(parent)
            self.strategyEngine = strategyEngine
            self.eventEngine = eventEngine
            self.strategyLoaded = False
            self.strategyType = strategyType
            self.initUi()
            self.updateMonitor(strategyType)
            self.resize(1600, 1600)


            # ----------------------------------------------------------------------

    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(gtext.STRATEGY)

        # 按钮
        newButton = QtWidgets.QPushButton(gtext.CREATE_INSTANCE)
        viewButton = QtWidgets.QPushButton(gtext.VIEW_STRATEGY)

        newButton.clicked.connect(self.newInstance)
        viewButton.clicked.connect(self.viewButton)
        buttonsBox = QtGui.QHBoxLayout()
        buttonsBox.addWidget(newButton)
        buttonsBox.addWidget(viewButton)
        buttonsBox.addStretch()



        # 滚动区域，放置strategyInstanceList
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        # self.strategyManager = CtaStrategyManager(self.strategyType)
        # w = QtGui.QWidget()
        # vbox = QtGui.QVBoxLayout()
        # vbox.addWidget(self.strategyTable)
        # vbox.addStretch()
        # w.setLayout(vbox)
        self.strategyTable = strategyInstanceTable(self)
        self.scrollArea.setWidget(self.strategyTable)
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










