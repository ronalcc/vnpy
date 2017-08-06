# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''
from vnpy.trader.app.strategy.uiStrategyListWidget import *
from vnpy.trader.app.strategy.uiStrategyInstanceListWidget import *

########################################################################
class UICtaInstanceListWidget(UIStrategyInstanceListWidget):
    """CTA策列列表"""

    #----------------------------------------------------------------------
    def __init__(self,strategtyEngine, eventEngine,strategyType, parent=None):
        """Constructor"""
        super(UICtaInstanceListWidget, self).__init__(strategtyEngine, eventEngine,strategyType,parent)


    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(gtext.STRATEGY_INSTANCE_LIST)
        # 滚动区域，放置strategyManager
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.strategyTable = CtaStrategyInstanceListMonitor(self.strategyEngine, self.eventEngine)
        self.scrollArea.setWidget(self.strategyTable)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.scrollArea)
        self.setLayout(vbox)

########################################################################
class CtaStrategyInstanceListMonitor(StrategyListMonitor):

    def __init__(self,strategtyEngine, eventEngine,strategyType, parent=None):
        pass

    
    



    
    