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
        self.strategyEngine = strategyEngine
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
        list = self.strategyEngine.mainEngine.dbQuery("strategy", "strategyInstance", {"strategyName": strategyName})
        if len(list) > 0:
            self.strategyTable.updateData(list)


########################################################################
class StrategyInstanceListMonitor(BasicMonitor):
    """表格"""

    # ----------------------------------------------------------------------
    def __init__(self, strategyEngine, eventEngine, parent=None):
        """Constructor"""
        super(StrategyInstanceListMonitor, self).__init__(strategyEngine, eventEngine, parent)

        # 设置表头有序字典
        d = OrderedDict()
        d['strategyName'] = {'chinese': stext.STRATEGYNAME, 'cellType': BasicCell}
        d['strategyInstanceName'] = {'chinese': stext.STRATEGY_INSTANCE, 'cellType': BasicCell}
        d['oper'] = {'chinese': stext.OPER, 'cellType': BasicCell}
        d['instanceStatus'] = {'chinese': stext.STRATEGY_INSTANCE_STATUS, 'cellType': BasicCell}
        d['startDate'] = {'chinese': stext.STARTDATE, 'cellType': BasicCell}
        d['endDate'] = {'chinese': stext.ENDDATE, 'cellType': BasicCell}
        d['comment'] = {'chinese': stext.COMMENT, 'cellType': BasicCell}
        self.setHeaderDict(d)

        # 设置数据键
        self.setDataKey('strategyInstanceName')

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
        super(StrategyInstanceListMonitor, self).initTable()

    #----------------------------------------------------------------------
    def updateData(self, list):
        self.setRowCount(len(list))
        row = 0
        while(row<len(list)):
               data = list[row]
               buttonInitInstance = QtWidgets.QPushButton(text.INIT)
               buttonStartInstance = QtWidgets.QPushButton(text.START)
               buttonViewInstance = QtWidgets.QPushButton(text.VIEW)
               buttonInitInstance.clicked.connect(lambda:self.initInstance(data['strategyInstanceName']))
               buttonStartInstance.clicked.connect(lambda:self.stratInstance(data['strategyInstanceName']))
               buttonViewInstance.clicked.connect(lambda:self.viewInstance(data['strategyInstanceName']))
               hbox = QtWidgets.QHBoxLayout()
               hbox.addWidget(buttonInitInstance)
               hbox.addWidget(buttonStartInstance)
               hbox.addWidget(buttonViewInstance)



               self.setItem(row,0,QtGui.QTableWidgetItem(unicode(data['strategyName'])))
               self.setItem(row, 1, QtGui.QTableWidgetItem(unicode(data['strategyInstanceName'])))
               self.setCellWidget(row,2,hbox)
               self.setItem(row, 3, QtGui.QTableWidgetItem(unicode(data['instanceStatus'])))
               self.setItem(row, 4, QtGui.QTableWidgetItem(unicode(data['startDate'])))
               self.setItem(row, 5, QtGui.QTableWidgetItem(unicode(data['endDate'])))
               self.setItem(row, 6, QtGui.QTableWidgetItem(unicode(data['comment'])))

               row +=1
        self.inited = True








