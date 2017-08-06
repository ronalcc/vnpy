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
from vnpy.trader.app.strategy.language import  text as stext


from vnpy.trader.app.strategy.language import text




#################################################################################################################
class UIStrategyInstanceListWidget(QtWidgets.QWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, strategyEngine, eventEngine, strategyClass, parent=None):
        """Constructor"""
        super(UIStrategyInstanceListWidget, self).__init__(parent)
        self.mainEngine = strategyEngine
        self.eventEngine = eventEngine
        self.strategyClass = strategyClass
        self.initUi()
        self.updateMonitor(strategyClass)
        self.resize(1600, 1600)

    # ----------------------------------------------------------------------
    @abstractmethod
    def initUi(self):
        """初始化界面"""
        pass


    # ----------------------------------------------------------------------
    def initAll(self):
        """全部初始化"""
        for name in self.ctaEngine.strategyDict.keys():
            self.ctaEngine.initStrategy(name)

            # ----------------------------------------------------------------------

    def startAll(self):
        """全部启动"""
        for name in self.ctaEngine.strategyDict.keys():
            self.ctaEngine.startStrategy(name)

    # ----------------------------------------------------------------------
    def stopAll(self):
        """全部停止"""
        for name in self.ctaEngine.strategyDict.keys():
            self.ctaEngine.stopStrategy(name)

    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtWidgets.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                               text.SAVE_POSITION_QUESTION, QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.ctaEngine.savePosition()

        event.accept()

    # ----------------------------------------------------------------------
    def updateMonitor(self, strategyType):
        """更新查询结果集"""
        list = self.strategyEngine.mainEngine.dbQuery("strategy", "strategyClass", {"strategyType": strategyType})
        if len(list) > 0:
            self.strategyTable.updateData(list)


########################################################################
class StrategyListMonitor(BasicMonitor):
    """表格"""

    # ----------------------------------------------------------------------
    def __init__(self, mainEngine, eventEngine, parent=None):
        """Constructor"""
        super(StrategyListMonitor, self).__init__(mainEngine, eventEngine, parent)

        # 设置表头有序字典
        d = OrderedDict()
        d['strategyName'] = {'chinese': stext.STRATEGYNAME, 'cellType': BasicCell}
        d['strategyType'] = {'chinese': stext.STRATEGYTYPE, 'cellType': BasicCell}
        d['comment'] = {'chinese': stext.COMMENT, 'cellType': BasicCell}
        d['author'] = {'chinese': stext.AUTHOR, 'cellType': BasicCell}
        d['oper'] = {'chinese': stext.OPER, 'cellType': BasicCell}
        self.setHeaderDict(d)

        # 设置数据键
        self.setDataKey('strategyName')

        # 设置监控事件类型
        self.setEventType(EVENT_TIMER)

        # 设置字体
        self.setFont(BASIC_FONT)

        # 设置允许排序
        self.setSorting(True)

        # 初始化表格
        self.initTable()

        # 注册事件监听
        self.registerEvent()


    #------------------------------------------------
    def initTable(self):
        super(StrategyListMonitor, self).initTable()

    #----------------------------------------------------------------------
    def updateData(self, list):
        self.setRowCount(len(list))
        #if not self.inited:

        row = 0
        while(row<len(list)):
               data = list[row]
               buttonInstanceManage = QtWidgets.QPushButton(gtext.INSTANCEMANAGE)
               buttonInstanceManage.clicked.connect(lambda:self.openStrategy(data['strategyClass']))
               self.setItem(row,0,QtGui.QTableWidgetItem(unicode(data['strategyClass'])))
               self.setItem(row, 1, QtGui.QTableWidgetItem(unicode(data['strategyType'])))
               self.setItem(row, 2, QtGui.QTableWidgetItem(unicode(data['comment'])))
               self.setItem(row, 3, QtGui.QTableWidgetItem(unicode(data['author'])))
               self.setCellWidget(row,4,buttonInstanceManage)
               row +=1
        self.inited = True

    #-----------------------------------------------------------------------------------------
    @abstractmethod
    def openStrategy(self,strategyClass):
        pass


    #------------------------------------------------------
    @abstractmethod
    def registerEvent(self):
        pass






