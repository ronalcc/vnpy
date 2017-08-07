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
        #查询输入区
        hbox1 = QtWidgets.QHBoxLayout()
        newButton = QtWidgets.QPushButton(text.BUTTON_NEW)
        searchButton = QtWidgets.QPushButton(text.BUTTON_SEARCH)
        newButton.clicked.connect(self.create)
        searchButton.clicked.connect(self.search)
        hbox1.addWidget(newButton)
        hbox1.addWidget(searchButton)





        #按钮区


        # 列表
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.strategyTable = CtaStrategyInstanceListMonitor(self.strategyEngine, self.eventEngine)
        self.scrollArea.setWidget(self.strategyTable)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.scrollArea)
        vbox.addWidget(hbox1)
        self.setLayout(vbox)

    #-----------------------------------------------------------
    def create(self):
        """创建策略实例"""
        pass

    #-----------------------------------------------------------
    def search(self):
        """条件查询"""
        pass

    #-----------------------------------------------------------
    def view(self,instanceId):
        """查看策略实例"""
        pass




########################################################################
class CtaStrategyInstanceListMonitor(StrategyListMonitor):

    def __init__(self,strategtyEngine, eventEngine, parent=None):
        pass

    
    



    
    