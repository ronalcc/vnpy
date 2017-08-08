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
    def __init__(self,strategtyEngine, eventEngine,strategyClass, parent=None):
        """Constructor"""
        super(UICtaInstanceListWidget, self).__init__(strategtyEngine, eventEngine,strategyClass,parent)


    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(gtext.STRATEGY_INSTANCE_LIST)
        #查询输入区
        hbox1 = QtWidgets.QHBoxLayout()
        newButton = QtWidgets.QPushButton(text.BUTTON_NEW)
        newButton.clicked.connect(self.create)
        self.combo = QtGui.QComboBox(self)
        self.combo.addItem(unicode("全部"))
        self.combo.addItem(unicode("运行"))
        self.combo.addItem(unicode("停止"))
        self.combo.addItem(unicode("废止"))
        self.connect(self.combo, QtCore.SIGNAL('activated(QString)'),self.onActivated)
        hbox1.addWidget(self.combo)
        hbox1.addWidget(newButton)
        hbox1.addStretch()




        #按钮区


        # 列表
        hbox2 = QtWidgets.QHBoxLayout()
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        self.strategyTable = CtaStrategyInstanceListMonitor(self.strategyEngine, self.eventEngine)
        scrollArea.setWidget(self.strategyTable)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox1)
        self.strategyTable.strategyClass = self.strategyClass
        vbox.addWidget(scrollArea)
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

    def onActivated(self):
        cindex = self.combo.currentIndex()
        strategyStatus = None
        if cindex==1:
            strategyStatus = '1'
        elif cindex==2:
            strategyStatus = '0'
        elif cindex == 3:
            strategyStatus = '2'
        else:
            strategyStatus = None

        self.updateMonitor(self.strategyClass, strategyStatus)

        self.strategyTable.strategyStatus = strategyStatus



            ########################################################################
class CtaStrategyInstanceListMonitor(StrategyInstanceListMonitor):

    def __init__(self,strategyEngine, eventEngine, parent=None):
        super(CtaStrategyInstanceListMonitor,self).__init__(strategyEngine,eventEngine,parent)


    #------------------------------------------------
    def initTable(self):
        super(CtaStrategyInstanceListMonitor, self).initTable()
        self.horizontalHeader().resizeSection(0,250)
        self.horizontalHeader().resizeSection(1,250)
        self.horizontalHeader().resizeSection(2,100)
        self.horizontalHeader().resizeSection(3,100)
        self.horizontalHeader().resizeSection(4,100)
        self.horizontalHeader().resizeSection(5, 150)
        self.horizontalHeader().resizeSection(6, 150)
        self.horizontalHeader().resizeSection(7, 150)
        self.horizontalHeader().resizeSection(8, 100)
        self.horizontalHeader().resizeSection(9, 100)
        self.horizontalHeader().resizeSection(10, 100)
        self.setColumnWidth(0,250)
        self.setColumnWidth(1,250)
        self.setColumnWidth(2,100)
        self.setColumnWidth(3,100)
        self.setColumnWidth(4,100)
        self.setColumnWidth(5, 150)
        self.setColumnWidth(6, 150)
        self.setColumnWidth(7, 150)
        self.setColumnWidth(8, 100)
        self.setColumnWidth(9, 100)
        self.setColumnWidth(10, 100)

        self.strategyClass=''
        self.instanceStatus=''


    #----------------------------------------------------------------------
    def updateEvent(self, event):
        """收到事件更新"""
        if self.instanceStatus == None:
            list = self.strategyEngine.mainEngine.dbQuery("strategy", "strategyInstance",
                                                          {"strategyClass": self.strategyClass})
        else:
            list = self.strategyEngine.mainEngine.dbQuery("strategy", "strategyInstance",
                                                          {"strategyClass": self.strategyClass,
                                                           "instanceStatus": self.instanceStatus})
        self.updateData(list)

    
    



    
    