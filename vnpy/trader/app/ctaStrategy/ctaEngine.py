# encoding: UTF-8

'''
本文件中实现了CTA策略引擎，针对CTA类型的策略，抽象简化了部分底层接口的功能。

关于平今和平昨规则：
1. 普通的平仓OFFSET_CLOSET等于平昨OFFSET_CLOSEYESTERDAY
2. 只有上期所的品种需要考虑平今和平昨的区别
3. 当上期所的期货有今仓时，调用Sell和Cover会使用OFFSET_CLOSETODAY，否则
   会使用OFFSET_CLOSE
4. 以上设计意味着如果Sell和Cover的数量超过今日持仓量时，会导致出错（即用户
   希望通过一个指令同时平今和平昨）
5. 采用以上设计的原因是考虑到vn.trader的用户主要是对TB、MC和金字塔类的平台
   感到功能不足的用户（即希望更高频的交易），交易策略不应该出现4中所述的情况
6. 对于想要实现4中所述情况的用户，需要实现一个策略信号引擎和交易委托引擎分开
   的定制化统结构（没错，得自己写）
'''

from __future__ import division

import json
import os
import traceback
from collections import OrderedDict
from datetime import datetime, timedelta

from vnpy.event import Event
from vnpy.trader.vtEvent import *
from vnpy.trader.vtConstant import *
from vnpy.trader.vtObject import VtTickData, VtBarData
from vnpy.trader.vtGateway import VtSubscribeReq, VtOrderReq, VtCancelOrderReq, VtLogData
from vnpy.trader.vtFunction import todayDate

from vnpy.trader.app.ctaStrategy.ctaBase import *
from vnpy.trader.app.ctaStrategy.strategy import STRATEGY_CLASS
from vnpy.trader.app.ctaStrategy.ctaTemplate import *
from vnpy.trader.app.strategy.strategyEngine import *



########################################################################
class CtaEngine(StrategyEngine):
    """CTA策略引擎"""


    #----------------------------------------------------------------------
    def __init__(self, mainEngine, eventEngine):
        """Constructor"""
        super(CtaEngine,self).__init__(mainEngine,eventEngine)
 
    #----------------------------------------------------------------------
    def sendOrder(self, symbol, orderType, price, volume, strategyInstance):
        """发单"""
        contract = self.mainEngine.getContract(symbol)

        req = VtOrderReq()
        req.symbol = contract.symbol
        req.exchange = contract.exchange
        req.price = self.roundToPriceTick(contract.priceTick, price)
        req.volume = volume

        req.productClass = contract.productClass
        req.currency = contract.currency
        
        # 设计为CTA引擎发出的委托只允许使用限价单
        req.priceType = constant.PRICETYPE_LIMITPRICE
        
        # CTA委托类型映射
        if orderType == CTAORDER_BUY:
            req.direction = constant.DIRECTION_LONG
            req.offset = constant.OFFSET_OPEN
            
        elif orderType == CTAORDER_SELL:
            req.direction = constant.DIRECTION_SHORT
            
            # 只有上期所才要考虑平今平昨
            if contract.exchange != constant.EXCHANGE_SHFE:
                req.offset = constant.OFFSET_CLOSE
            else:
                # 获取持仓缓存数据
                posBuffer = self.posBufferDict.get(symbol, None)
                # 如果获取持仓缓存失败，则默认平昨
                if not posBuffer:
                    req.offset = constant.OFFSET_CLOSE
                # 否则如果有多头今仓，则使用平今
                elif posBuffer.longToday:
                    req.offset= constant.OFFSET_CLOSETODAY
                # 其他情况使用平昨
                else:
                    req.offset =constant.OFFSET_CLOSE
                
        elif orderType == CTAORDER_SHORT:
            req.direction = constant.DIRECTION_SHORT
            req.offset = constant.OFFSET_OPEN
            
        elif orderType == CTAORDER_COVER:
            req.direction = constant.DIRECTION_LONG
            
            # 只有上期所才要考虑平今平昨
            if contract.exchange != constant.EXCHANGE_SHFE:
                req.offset = constant.OFFSET_CLOSE
            else:
                # 获取持仓缓存数据
                posBuffer = self.posBufferDict.get(symbol, None)
                # 如果获取持仓缓存失败，则默认平昨
                if not posBuffer:
                    req.offset = constant.OFFSET_CLOSE
                # 否则如果有空头今仓，则使用平今
                elif posBuffer.shortToday:
                    req.offset= constant.OFFSET_CLOSETODAY
                # 其他情况使用平昨
                else:
                    req.offset = constant.OFFSET_CLOSE
        
        return super.sendOrder()
        

    
    #----------------------------------------------------------------------
    def cancelOrder(self, vtOrderID):
        """撤单"""
        # 查询报单对象
        super.cancelOrder(self,vtOrderID)

    #----------------------------------------------------------------------
    def sendStopOrder(self, vtSymbol, orderType, price, volume, strategyInstance):
        """发停止单（本地实现）"""
        self.stopOrderCount += 1
        stopOrderID = STOPORDERPREFIX + str(self.stopOrderCount)
        
        so = StopOrder()
        so.vtSymbol = vtSymbol
        so.orderType = orderType
        so.price = price
        so.volume = volume
        so.strategy = strategyInstance
        so.stopOrderID = stopOrderID
        so.status = STOPORDER_WAITING
        
        if orderType == CTAORDER_BUY:
            so.direction = constant.DIRECTION_LONG
            so.offset = constant.OFFSET_OPEN
        elif orderType == CTAORDER_SELL:
            so.direction = constant.DIRECTION_SHORT
            so.offset = constant.OFFSET_CLOSE
        elif orderType == CTAORDER_SHORT:
            so.direction = constant.DIRECTION_SHORT
            so.offset = constant.OFFSET_OPEN
        elif orderType == CTAORDER_COVER:
            so.direction = constant.DIRECTION_LONG
            so.offset = constant.OFFSET_CLOSE
        super.sendStopOrder(self,so)
        return stopOrderID

    
    #----------------------------------------------------------------------
    def cancelStopOrder(self, stopOrderID):
        """撤销停止单"""
        # 检查停止单是否存在
        super.cancelStopOrder(self,stopOrderID)

    #----------------------------------------------------------------------
    def processStopOrder(self, tick):
        """收到行情后处理本地停止单（检查是否要立即发出）"""
        # vtSymbol = tick.vtSymbol
        #
        # # 首先检查是否有策略交易该合约
        # if vtSymbol in self.tickStrategyDict:
        #     # 遍历等待中的停止单，检查是否会被触发
        #     for so in self.workingStopOrderDict.values():
        #         if so.vtSymbol == vtSymbol:
        #             longTriggered = so.direction==constant.DIRECTION_LONG and tick.lastPrice>=so.price        # 多头停止单被触发
        #             shortTriggered = so.direction==constant.DIRECTION_SHORT and tick.lastPrice<=so.price     # 空头停止单被触发
        #
        #             if longTriggered or shortTriggered:
        #                 # 买入和卖出分别以涨停跌停价发单（模拟市价单）
        #                 if so.direction==constant.DIRECTION_LONG:
        #                     price = tick.upperLimit
        #                 else:
        #                     price = tick.lowerLimit
        #
        #                 so.status = STOPORDER_TRIGGERED
        #                 self.sendOrder(so.vtSymbol, so.orderType, price, so.volume, so.strategy)
        #                 del self.workingStopOrderDict[so.stopOrderID]

    #----------------------------------------------------------------------
    def processTickEvent(self, event):
        """处理行情推送"""
        # tick = event.dict_['data']
        # # 收到tick行情后，先处理本地停止单（检查是否要立即发出）
        # self.processStopOrder(tick)
        #
        # # 推送tick到对应的策略实例进行处理
        # if tick.vtSymbol in self.tickStrategyDict:
        #     # 添加datetime字段
        #     if not tick.datetime:
        #         tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')
        #
        #     # 逐个推送到策略实例中
        #     l = self.tickStrategyDict[tick.vtSymbol]
        #     for strategy in l:
        #         self.callStrategyFunc(strategy, strategy.onTick, tick)
    
    #----------------------------------------------------------------------
    def processOrderEvent(self, event):
        """处理委托推送"""
        # order = event.dict_['data']
        #
        # if order.vtOrderID in self.orderStrategyDict:
        #     strategy = self.orderStrategyDict[order.vtOrderID]
        #     self.callStrategyFunc(strategy, strategy.onOrder, order)
    
    #----------------------------------------------------------------------
    def processTradeEvent(self, event):
        """处理成交推送"""
        # trade = event.dict_['data']
        #
        # # 过滤已经收到过的成交回报
        # if trade.vtTradeID in self.tradeSet:
        #     return
        # self.tradeSet.add(trade.vtTradeID)
        #
        # # 将成交推送到策略对象中
        # if trade.vtOrderID in self.orderStrategyDict:
        #     strategy = self.orderStrategyDict[trade.vtOrderID]
        #
        #     # 计算策略持仓
        #     if trade.direction == constant.DIRECTION_LONG:
        #         strategy.pos += trade.volume
        #     else:
        #         strategy.pos -= trade.volume
        #
        #     self.callStrategyFunc(strategy, strategy.onTrade, trade)
        #
        # # 更新持仓缓存数据
        # if trade.vtSymbol in self.tickStrategyDict:
        #     posBuffer = self.posBufferDict.get(trade.vtSymbol, None)
        #     if not posBuffer:
        #         posBuffer = PositionBuffer()
        #         posBuffer.vtSymbol = trade.vtSymbol
        #         self.posBufferDict[trade.vtSymbol] = posBuffer
        #     posBuffer.updateTradeData(trade)
            
    #----------------------------------------------------------------------
    def processPositionEvent(self, event):
        """处理持仓推送"""
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
    
    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.eventEngine.register(EVENT_TICK, self.processTickEvent)
        self.eventEngine.register(EVENT_ORDER, self.processOrderEvent)
        self.eventEngine.register(EVENT_TRADE, self.processTradeEvent)
        self.eventEngine.register(EVENT_POSITION, self.processPositionEvent)
 
    #----------------------------------------------------------------------
    def insertData(self, dbName, collectionName, data):
        """插入数据到数据库（这里的data可以是VtTickData或者VtBarData）"""
        self.mainEngine.dbInsert(dbName, collectionName, data.__dict__)
    
    #----------------------------------------------------------------------
    def loadBar(self, dbName, collectionName, days):
        """从数据库中读取Bar数据，startDate是datetime对象"""
        startDate = self.today - timedelta(days)
        
        d = {'datetime':{'$gte':startDate}}
        barData = self.mainEngine.dbQuery(dbName, collectionName, d)
        
        l = []
        for d in barData:
            bar = VtBarData()
            bar.__dict__ = d
            l.append(bar)
        return l
    
    #----------------------------------------------------------------------
    def loadTick(self, dbName, collectionName, days):
        """从数据库中读取Tick数据，startDate是datetime对象"""
        startDate = self.today - timedelta(days)
        
        d = {'datetime':{'$gte':startDate}}
        tickData = self.mainEngine.dbQuery(dbName, collectionName, d)
        
        l = []
        for d in tickData:
            tick = VtTickData()
            tick.__dict__ = d
            l.append(tick)
        return l    
    
    #----------------------------------------------------------------------
    def writeCtaLog(self, content):
        """快速发出CTA模块日志事件"""
        log = VtLogData()
        log.logContent = content
        event = Event(type_=EVENT_CTA_LOG)
        event.dict_['data'] = log
        self.eventEngine.put(event)   
    
    #----------------------------------------------------------------------
    def loadStrategy(self, l):
       for strategy in l:
          try:
            name = strategy['strategyName']
            className = strategy['strategyName']

          except Exception, e:
            self.writeCtaLog(u'载入策略出错：%s' %e)
            return
        
        # 获取策略类
          strategyClass = STRATEGY_CLASS.get(className, None)
          if not strategyClass:
            self.writeCtaLog(u'找不到策略类：%s' %className)
            return
        
          # 防止策略重名
          if name in self.strategyDict:
            self.writeCtaLog(u'策略实例重名：%s' %name)
          else:
            # 创建策略实例
            strategy = strategyClass(self, strategy)
            self.strategyDict[name] = strategy


            # # 保存Tick映射关系
            # if strategy.vtSymbol in self.tickStrategyDict:
            #     l = self.tickStrategyDict[strategy.vtSymbol]
            # else:
            #     l = []
            #     self.tickStrategyDict[strategy.vtSymbol] = l
            # l.append(strategy)
            #
            # # 订阅合约
            # contract = self.mainEngine.getContract(strategy.vtSymbol)
            # if contract:
            #     req = VtSubscribeReq()
            #     req.symbol = contract.symbol
            #     req.exchange = contract.exchange
            #
            #     # 对于IB接口订阅行情时所需的货币和产品类型，从策略属性中获取
            #     req.currency = strategy.currency
            #     req.productClass = strategy.productClass
            #
            #     self.mainEngine.subscribe(req, contract.gatewayName)
            # else:
            #     self.writeCtaLog(u'%s的交易合约%s无法找到' %(name, strategy.vtSymbol))

    #----------------------------------------------------------------------
    def initStrategy(self, name):
        """初始化策略"""
        if name in self.strategyDict:
            strategy = self.strategyDict[name]
            
            if not strategy.inited:
                strategy.inited = True
                self.callStrategyFunc(strategy, strategy.onInit)
            else:
                self.writeCtaLog(u'请勿重复初始化策略实例：%s' %name)
        else:
            self.writeCtaLog(u'策略实例不存在：%s' %name)        

    #---------------------------------------------------------------------
    def startStrategy(self, name):
        """启动策略"""
        if name in self.strategyDict:
            strategy = self.strategyDict[name]
            
            if strategy.inited and not strategy.trading:
                strategy.trading = True
                self.callStrategyFunc(strategy, strategy.onStart)
        else:
            self.writeCtaLog(u'策略实例不存在：%s' %name)
    
    #----------------------------------------------------------------------
    def stopStrategy(self, name):
        """停止策略"""
        if name in self.strategyDict:
            strategy = self.strategyDict[name]
            
            if strategy.trading:
                strategy.trading = False
                self.callStrategyFunc(strategy, strategy.onStop)
                
                # 对该策略发出的所有限价单进行撤单
                for vtOrderID, s in self.orderStrategyDict.items():
                    if s is strategy:
                        self.cancelOrder(vtOrderID)
                
                # 对该策略发出的所有本地停止单撤单
                for stopOrderID, so in self.workingStopOrderDict.items():
                    if so.strategy is strategy:
                        self.cancelStopOrder(stopOrderID)   
        else:
            self.writeCtaLog(u'策略实例不存在：%s' %name)        
    
    #----------------------------------------------------------------------
    def saveSetting(self):
        """保存策略配置"""
        with open(self.settingFileName, 'w') as f:
            l = []
            
            for strategy in self.strategyDict.values():
                setting = {}
                for param in strategy.paramList:
                    setting[param] = strategy.__getattribute__(param)
                l.append(setting)
            
            jsonL = json.dumps(l, indent=4)
            f.write(jsonL)
    
    #----------------------------------------------------------------------
    """
    def loadSetting(self):
        with open(self.settingFileName) as f:
            l = json.load(f)
            
            for setting in l:
                self.loadStrategy(setting)
                
        self.loadPosition()
    """
    # ------------------数据库读取策略----------------------------------------------------
    def querySetting(self):
       findDict = {"strategyType":"CTA"}
       l = self.mainEngine.dbQuery('strategy','strategyClass',findDict)

       return l

    #----------------------------------------------------------------------
    def getStrategyVar(self, name):
        """获取策略当前的变量字典"""
        if name in self.strategyDict:
            strategy = self.strategyDict[name]
            varDict = OrderedDict()
            
            for key in strategy.varList:
                varDict[key] = strategy.__getattribute__(key)
            
            return varDict
        else:
            self.writeCtaLog(u'策略实例不存在：' + name)    
            return None
    
    #--------------------------------------deprecated--------------------------------
    def getStrategyParam(self, name):
        """获取策略的参数字典"""
        if name in self.strategyDict:
            strategy = self.strategyDict[name]
            paramDict = OrderedDict()
            
            for key in strategy.paramList:  
                paramDict[key] = strategy.__getattribute__(key)
            
            return paramDict
        else:
            self.writeCtaLog(u'策略实例不存在：' + name)    
            return None   


    #----------------------------------------------------------------------
    def putStrategyEvent(self, name):
        """触发策略状态变化事件（通常用于通知GUI更新）"""
        event = Event(EVENT_CTA_STRATEGY+name)
        self.eventEngine.put(event)
        
    #----------------------------------------------------------------------
    def callStrategyFunc(self, strategy, func, params=None):
        """调用策略的函数，若触发异常则捕捉"""
        try:
            if params:
                func(params)
            else:
                func()
        except Exception:
            # 停止策略，修改状态为未初始化
            strategy.trading = False
            strategy.inited = False
            
            # 发出日志
            content = '\n'.join([u'策略%s触发异常已停止' %strategy.name,
                                traceback.format_exc()])
            self.writeCtaLog(content)
            
    #----------------------------------------------------------------------
    def savePosition(self):
        """保存所有策略的持仓情况到数据库"""
        for strategy in self.strategyDict.values():
            flt = {'name': strategy.name,
                   'vtSymbol': strategy.vtSymbol}
            
            d = {'name': strategy.name,
                 'vtSymbol': strategy.vtSymbol,
                 'pos': strategy.pos}
            
            self.mainEngine.dbUpdate(POSITION_DB_NAME, strategy.className,
                                     d, flt, True)
            
            content = '策略%s持仓保存成功' %strategy.name
            self.writeCtaLog(content)
    
    #----------------------------------------------------------------------
    def loadPosition(self):
        """从数据库载入策略的持仓情况"""
        for strategy in self.strategyDict.values():
            flt = {'name': strategy.name,
                   'vtSymbol': strategy.vtSymbol}
            posData = self.mainEngine.dbQuery(POSITION_DB_NAME, strategy.className, flt)
            
            for d in posData:
                strategy.pos = d['pos']
                
    #----------------------------------------------------------------------
    def roundToPriceTick(self, priceTick, price):
        """取整价格到合约最小价格变动"""
        if not priceTick:
            return price
        
        newPrice = round(price/priceTick, 0) * priceTick
        return newPrice    
    
    #----------------------------------------------------------------------
    def stop(self):
        """停止"""
        pass


########################################################################
class PositionBuffer(object):
    """持仓缓存信息（本地维护的持仓数据）"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.vtSymbol = EMPTY_STRING
        
        # 多头
        self.longPosition = EMPTY_INT
        self.longToday = EMPTY_INT
        self.longYd = EMPTY_INT
        
        # 空头
        self.shortPosition = EMPTY_INT
        self.shortToday = EMPTY_INT
        self.shortYd = EMPTY_INT
        
    #----------------------------------------------------------------------
    def updatePositionData(self, pos):
        """更新持仓数据"""
        if pos.direction == DIRECTION_LONG:
            self.longPosition = pos.position
            self.longYd = pos.ydPosition
            self.longToday = self.longPosition - self.longYd
        else:
            self.shortPosition = pos.position
            self.shortYd = pos.ydPosition
            self.shortToday = self.shortPosition - self.shortYd
    
    #----------------------------------------------------------------------
    def updateTradeData(self, trade):
        """更新成交数据"""
        if trade.direction == DIRECTION_LONG:
            # 多方开仓，则对应多头的持仓和今仓增加
            if trade.offset == OFFSET_OPEN:
                self.longPosition += trade.volume
                self.longToday += trade.volume
            # 多方平今，对应空头的持仓和今仓减少
            elif trade.offset == OFFSET_CLOSETODAY:
                self.shortPosition -= trade.volume
                self.shortToday -= trade.volume
            # 多方平昨，对应空头的持仓和昨仓减少
            else:
                self.shortPosition -= trade.volume
                self.shortYd -= trade.volume
        else:
            # 空头和多头相同
            if trade.offset == OFFSET_OPEN:
                self.shortPosition += trade.volume
                self.shortToday += trade.volume
            elif trade.offset == OFFSET_CLOSETODAY:
                self.longPosition -= trade.volume
                self.longToday -= trade.volume
            else:
                self.longPosition -= trade.volume
                self.longYd -= trade.volume
        
        
    
    


