# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''

from vnpy.trader.uiBasicWidget import *
from vnpy.event import Event
from vnpy.trader.vtEvent import *
from PyQt4 import QtGui
from vnpy.trader.app.strategy.uiStrategyWidget import *
from vnpy.trader.app.strategy.language import  text as stext
from vnpy.trader.app.ctaStrategy.language import text
from vnpy.trader.language import text as gtext

########################################################################
class CtaValueMonitor(BasicMonitor):
    """表格"""

    # ----------------------------------------------------------------------
    def __init__(self, mainEngine, eventEngine, parent=None):
        """Constructor"""
        super(MarketMonitor, self).__init__(mainEngine, eventEngine, parent)

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
        self.setEventType(EVENT_TICK)

        # 设置字体
        self.setFont(BASIC_FONT)

        # 设置允许排序
        self.setSorting(True)

        # 初始化表格
        self.initTable()

        # 注册事件监听
        self.registerEvent()




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
        self.setRowCount(1)
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
        # else:
        #     row = 0
        #     while(row<len(list)):
        #       data = list[row]
        #       buttonInstanceManage = QtWidgets.QPushButton(gtext.INSTANCEMANAGE)
        #       self.item(row,0).setText(unicode(data['strategyName']))
        #       self.item(row,1).setText(unicode(data['strategyType']))
        #       self.item(row, 2).setText(unicode(data['comment']))
        #       self.item(row, 3).setText(unicode(data['author']))

    #-----------------------------------------------------------------------------------------
    def openStrategy(self,strategyClass):
        pass




########################################################################
class CtaEngineManager(QtWidgets.QWidget):
    """CTA引擎管理组件"""

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine,strategyType, parent=None):
        """Constructor"""
        super(CtaEngineManager, self).__init__(parent)
        self.strategyEngine = ctaEngine
        self.eventEngine = eventEngine
        self.strategyLoaded = False
        self.strategyType = strategyType
        self.initUi()
        self.updateMonitor(strategyType)
        self.resize(1600,1600)


    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(gtext.STRATEGY)

        # 按钮
        newButton = QtWidgets.QPushButton(text.LOAD_STRATEGY)
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
        #self.strategyManager = CtaStrategyManager(self.strategyType)
        # w = QtGui.QWidget()
        # vbox = QtGui.QVBoxLayout()
        # vbox.addWidget(self.strategyTable)
        # vbox.addStretch()
        # w.setLayout(vbox)
        self.strategyTable = CtaValueMonitor(self,self.strategyEngine.mainEngine,self.eventEngine)
        self.scrollArea.setWidget( self.strategyTable)
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
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtWidgets.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                           text.SAVE_POSITION_QUESTION, QtWidgets.QMessageBox.Yes | 
                                           QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    
        if reply == QtWidgets.QMessageBox.Yes: 
            self.ctaEngine.savePosition()
            
        event.accept()
        
        
    #----------------------------------------------------------------------
    def updateMonitor(self,strategyType):
        """更新查询结果集"""
        list = self.strategyEngine.mainEngine.dbQuery("strategy", "strategyClass", {"strategyType": strategyType})
        if len(list)>0:
          self.strategyTable.updateData(list)
    
    
    



    
    