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
class StrategyManager(QtWidgets.QGroupBox):
    """策略管理组件"""
    signal = QtCore.Signal(type(Event()))

    # ----------------------------------------------------------------------
    def __init__(self,name,parent=None):
        """Constructor"""
        super(StrategyManager, self).__init__(parent)
        self.name = name

        self.initUi()
        # self.updateMonitor()
        # self.registerEvent()

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

    def __init__(self, parent=None):
        pass
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










