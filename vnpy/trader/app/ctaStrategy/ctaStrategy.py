# encoding: UTF-8

'''
本文件包含了CTA引擎中的策略开发用模板，开发策略时需要继承CtaTemplate类。
'''
from abc import ABCMeta,abstractmethod,abstractproperty
from vnpy.trader.app.strategy.strategy import Strategy
from vnpy.trader.app.ctaStrategy.ctaBase import *


########################################################################
class CtaStrategy(Strategy):
    """CTA策略模板"""


    #----------------------------------------------------------------------
    def __init__(self, strategyEngine, strategyInstance):
        """Constructor"""
        super(CtaStrategy,self).__init__(strategyEngine,strategyInstance)


    # # ----------------------------------------------------------------------
    def processTicks(self,ticks):
        """收到组合行情推送后的回调方法"""

        #先处理停止单
        self.processStopOrder(ticks)
        self.onTicks(ticks)


    # # ----------------------------------------------------------------------
    def processOrder(self,event):
        """收到订单回报后的回调方法"""
        self.onOrder(event)

    # ----------------------------------------------------------------------

    def processTrade(self,event):
        """收到订成交回报后的回调方法"""
        trade = event.dict_['data']

        # 过滤已经收到过的成交回报
        if trade.vtTradeID in self.tradeSet:
            return
        self.tradeSet.add(trade.vtTradeID)

        # 将成交推送到策略对象中
        if trade.vtOrderID in self.orderStrategyDict:
            strategy = self.orderStrategyDict[trade.vtOrderID]

            # 计算策略持仓
            if trade.direction == constant.DIRECTION_LONG:
                strategy.pos += trade.volume
            else:
                strategy.pos -= trade.volume

            self.onTrade()

        # 更新持仓缓存数据
        if trade.vtSymbol in self.tickStrategyDict:
            posBuffer = self.posBufferDict.get(trade.vtSymbol, None)
            if not posBuffer:
                posBuffer = PositionBuffer()
                posBuffer.vtSymbol = trade.vtSymbol
                self.posBufferDict[trade.vtSymbol] = posBuffer
            posBuffer.updateTradeData(trade)

    # ----------------------------------------------------------------------

    def processPosition(self,position):
        """处理持仓推送"""
        pass
        # pos = event.dict_['data']
        #
        # # 更新持仓缓存数据
        # if pos.vtSymbol in self.tickStrategyDict:
        #     posBuffer = self.posBufferDict.get(pos.vtSymbol, None)
        #     if not posBuffer:
        #         posBuffer = PositionBuffer()
        #         posBuffer.vtSymbol = pos.vtSymbol
        #         self.posBufferDict[pos.vtSymbol] = posBuffer
        #     posBuffer.updatePositionData(pos)

    @abstractmethod
    def onTicks(self, ticks):
        """tick处理函数"""
        pass

    @abstractmethod
    def onOrder(self,order):
        pass

    @abstractmethod
    def onTrade(self,trade):
        pass

    @abstractmethod
    def onPosition(self,position):
        pass

    @abstractmethod
    def processStopOrder(self,ticks):
        pass
    #----------------------------------------------------------------------
    def buy(self, price, volume, stop=False):
        """买开"""
        return self.sendOrder(CTAORDER_BUY, price, volume, stop)
    
    #----------------------------------------------------------------------
    def sell(self, price, volume, stop=False):
        """卖平"""
        return self.sendOrder(CTAORDER_SELL, price, volume, stop)       

    #----------------------------------------------------------------------
    def short(self, price, volume, stop=False):
        """卖开"""
        return self.sendOrder(CTAORDER_SHORT, price, volume, stop)          
 
    #----------------------------------------------------------------------
    def cover(self, price, volume, stop=False):
        """买平"""
        return self.sendOrder(CTAORDER_COVER, price, volume, stop)
        
    #----------------------------------------------------------------------
    def sendOrder(self, orderType, price, volume, stop=False):
        """发送委托"""
        if self.trading:
            # 如果stop为True，则意味着发本地停止单
            if stop:
                vtOrderID = self.ctaEngine.sendStopOrder(self.vtSymbol, orderType, price, volume, self)
            else:
                vtOrderID = self.ctaEngine.sendOrder(self.vtSymbol, orderType, price, volume, self) 
            return vtOrderID
        else:
            # 交易停止时发单返回空字符串
            return ''        
        
    #----------------------------------------------------------------------
    def cancelOrder(self, vtOrderID):
        """撤单"""
        # 如果发单号为空字符串，则不进行后续操作
        if not vtOrderID:
            return
        
        if STOPORDERPREFIX in vtOrderID:
            self.ctaEngine.cancelStopOrder(vtOrderID)
        else:
            self.ctaEngine.cancelOrder(vtOrderID)
    
    #----------------------------------------------------------------------
    def insertTick(self, tick):
        """向数据库中插入tick数据"""
        self.ctaEngine.insertData(self.tickDbName, self.vtSymbol, tick)
    
    #----------------------------------------------------------------------
    def insertBar(self, bar):
        """向数据库中插入bar数据"""
        self.ctaEngine.insertData(self.barDbName, self.vtSymbol, bar)
        
    #----------------------------------------------------------------------
    def loadTick(self, days):
        """读取tick数据"""
        return self.ctaEngine.loadTick(self.tickDbName, self.vtSymbol, days)
    
    #----------------------------------------------------------------------
    def loadBar(self, days):
        """读取bar数据"""
        return self.ctaEngine.loadBar(self.barDbName, self.vtSymbol, days)
    
    #----------------------------------------------------------------------
    def writeCtaLog(self, content):
        """记录CTA日志"""
        content = self.name + ':' + content
        self.ctaEngine.writeCtaLog(content)
        
    #----------------------------------------------------------------------
    def putEvent(self):
        """发出策略状态变化事件"""
        self.ctaEngine.putStrategyEvent(self.name)
        
    #----------------------------------------------------------------------
    def getEngineType(self):
        """查询当前运行的环境"""
        return self.ctaEngine.engineType
    

########################################################################
# class TargetPosTemplate(CtaStrategy):
#     """
#     允许直接通过修改目标持仓来实现交易的策略模板
#
#     开发策略时，无需再调用buy/sell/cover/short这些具体的委托指令，
#     只需在策略逻辑运行完成后调用setTargetPos设置目标持仓，底层算法
#     会自动完成相关交易，适合不擅长管理交易挂撤单细节的用户。
#
#     使用该模板开发策略时，请在以下回调方法中先调用母类的方法：
#     onTick
#     onBar
#     onOrder
#
#     假设策略名为TestStrategy，请在onTick回调中加上：
#     super(TestStrategy, self).onTick(tick)
#
#     其他方法类同。
#     """
#
#     className = 'TargetPosTemplate'
#     author = u'量衍投资'
#
#     # 目标持仓模板的基本变量
#     tickAdd = 1             # 委托时相对基准价格的超价
#     lastTick = None         # 最新tick数据
#     lastBar = None          # 最新bar数据
#     targetPos = EMPTY_INT   # 目标持仓
#     orderList = []          # 委托号列表
#
#     # 变量列表，保存了变量的名称
#     varList = ['inited',
#                'trading',
#                'pos',
#                'targetPos']
#
#     #----------------------------------------------------------------------
#     def __init__(self, ctaEngine, setting):
#         """Constructor"""
#         super(TargetPosTemplate, self).__init__(ctaEngine, setting)
#
#     #----------------------------------------------------------------------
#     def onTick(self, tick):
#         """收到行情推送"""
#         self.lastTick = tick
#
#         # 实盘模式下，启动交易后，需要根据tick的实时推送执行自动开平仓操作
#         if self.trading:
#             self.trade()
#
#     #----------------------------------------------------------------------
#     def onBar(self, bar):
#         """收到K线推送"""
#         self.lastBar = bar
#
#     #----------------------------------------------------------------------
#     def onOrder(self, order):
#         """收到委托推送"""
#         if order.status == STATUS_ALLTRADED or order.status == STATUS_CANCELLED:
#             self.orderList.remove(order.vtOrderID)
#
#     #----------------------------------------------------------------------
#     def setTargetPos(self, targetPos):
#         """设置目标仓位"""
#         self.targetPos = targetPos
#
#         self.trade()
#
#     #----------------------------------------------------------------------
#     def trade(self):
#         """执行交易"""
#         # 先撤销之前的委托
#         for vtOrderID in self.orderList:
#             self.cancelOrder(vtOrderID)
#         self.orderList = []
#
#         # 如果目标仓位和实际仓位一致，则不进行任何操作
#         posChange = self.targetPos - self.pos
#         if not posChange:
#             return
#
#         # 确定委托基准价格，有tick数据时优先使用，否则使用bar
#         longPrice = 0
#         shortPrice = 0
#
#         if self.lastTick:
#             if posChange > 0:
#                 longPrice = self.lastTick.askPrice1 + self.tickAdd
#             else:
#                 shortPrice = self.lastTick.bidPrice1 - self.tickAdd
#         else:
#             if posChange > 0:
#                 longPrice = self.lastBar.close + self.tickAdd
#             else:
#                 shortPrice = self.lastBar.close - self.tickAdd
#
#         # 回测模式下，采用合并平仓和反向开仓委托的方式
#         if self.getEngineType() == ENGINETYPE_BACKTESTING:
#             if posChange > 0:
#                 vtOrderID = self.buy(longPrice, abs(posChange))
#             else:
#                 vtOrderID = self.short(shortPrice, abs(posChange))
#             self.orderList.append(vtOrderID)
#
#         # 实盘模式下，首先确保之前的委托都已经结束（全成、撤销）
#         # 然后先发平仓委托，等待成交后，再发送新的开仓委托
#         else:
#             # 检查之前委托都已结束
#             if self.orderList:
#                 return
#
#             # 买入
#             if posChange > 0:
#                 if self.pos < 0:
#                     vtOrderID = self.cover(longPrice, abs(self.pos))
#                 else:
#                     vtOrderID = self.buy(longPrice, abs(posChange))
#             # 卖出
#             else:
#                 if self.pos > 0:
#                     vtOrderID = self.sell(shortPrice, abs(self.pos))
#                 else:
#                     vtOrderID = self.short(shortPrice, abs(posChange))
#             self.orderList.append(vtOrderID)
    