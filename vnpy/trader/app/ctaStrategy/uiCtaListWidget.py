# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''

from vnpy.trader.uiBasicWidget import *
from vnpy.event import Event
from vnpy.trader.vtEvent import *
from PyQt4 import QtGui
from vnpy.trader.app.strategy.uiStrategyListWidget import *
from vnpy.trader.app.strategy.language import  text as stext
from vnpy.trader.app.ctaStrategy.language import text
from vnpy.trader.language import text as gtext
from vnpy.trader.app.ctaStrategy.uiCtaInstanceListWidget import *
########################################################################
class UICtaListWidget(UIStrategyListWidget):
    """CTA策列列表"""

    #----------------------------------------------------------------------
    def __init__(self,strategtyEngine, eventEngine,strategyType, parent=None):
        """Constructor"""
        super(UICtaListWidget, self).__init__(strategtyEngine, eventEngine,strategyType,parent)


    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(gtext.STRATEGY)
        # 滚动区域，放置strategyManager
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.strategyTable = CtaStrategyListMonitor(self.strategyEngine.mainEngine,self.eventEngine,self.strategyEngine)
        self.scrollArea.setWidget(self.strategyTable)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.scrollArea)
        self.setLayout(vbox)

########################################################################
class CtaStrategyListMonitor(StrategyListMonitor):
    """表格"""
    def __init__(self, mainEngine, eventEngine,strategyEngine=None,parent=None):
        """Constructor"""
        super(CtaStrategyListMonitor, self).__init__(mainEngine,eventEngine,strategyEngine)


    #------------------------------------------------
    def initTable(self):
        super(CtaStrategyListMonitor, self).initTable()
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


    #-----------------------------------------------------------------------------------------
    def openStrategy(self,strategyClass):
        self.ctaInstanceListWidget = UICtaInstanceListWidget(self.strategyEngine, self.eventEngine,strategyClass)
        self.ctaInstanceListWidget.show()
    



    
    