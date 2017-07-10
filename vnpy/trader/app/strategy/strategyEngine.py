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
from vnpy.trader.vtObject import VtTickData, VtBarData
from vnpy.trader.vtGateway import VtSubscribeReq, VtOrderReq, VtCancelOrderReq, VtLogData
from vnpy.trader.vtFunction import todayDate
from threading import Thread
from abc import ABCMeta,abstractmethod,abstractproperty


########################################################################
class StrategyEngine():
    """策略引擎"""

    # ----------------------------------------------------------------------
    def __init__(self, mainEngine, eventEngine):
        """Constructor"""
        self.mainEngine = mainEngine
        self.eventEngine = eventEngine

        # 当前日期
        self.today = todayDate()

        # 保存策略实例的字典
        # key为策略名称，value为策略对象，注意策略名称不允许重复
        self.strategyDict = {}

        # 保存vtSymbol和策略实例映射的字典（用于推送tick数据）
        # 由于可能多个strategy交易同一个vtSymbol，因此key为vtSymbol
        # value为包含所有相关strategy对象的list
        #self.tickStrategyDict = {}

        # 保存vtOrderID和strategy对象映射的字典（用于推送order和trade数据）
        # key为vtOrderID，value为strategy对象
        #self.orderStrategyDict = {}

        # 本地停止单编号计数
        self.stopOrderCount = 0
        # stopOrderID = STOPORDERPREFIX + str(stopOrderCount)

        # 本地停止单字典
        # key为stopOrderID，value为stopOrder对象
        self.stopOrderDict = {}  # 停止单撤销后不会从本字典中删除
        self.workingStopOrderDict = {}  # 停止单撤销后会从本字典中删除

        # 持仓缓存字典
        # key为vtSymbol，value为PositionBuffer对象
        self.posBufferDict = {}

        # 成交号集合，用来过滤已经收到过的成交推送
        self.tradeSet = set()

        # 引擎类型为实盘
        self.engineType = ENGINETYPE_TRADING



        #策略引擎的线程数量
        self.strategyThreadNum = 0;

    #------------------------------------------------------------------------
    def getThread(self,method):
        #获取线程
        if self.strategyThreadNum == 0:
              return Thread(target=method)



    # ----------------------------------------------------------------------------
    def loadStrategy(self, _id):
        #防止策略重复载入
        if _id in self.strategyDict:
            self.writeCtaLog(u'策略实例已载入：%s' % name)
            strategy = self.strategyDict[_id]
        else:
            # 创建策略实例
            strategyInstance = self.mainEngine.dbQuery("strategy", "strategyInstance", {"_id": _id})
            strategyClass = STRATEGY_CLASS.get(strategyInstance['strategyName'], None)
            strategy = strategyClass(self, strategyInstance)
            self.callStrategyFunc(strategy, strategy.onLoadStrategy)

            self.strategyDict[_id] = strategy
        return strategy

    # ---------------------------------------------------------------------

    def startStrategy(self, _id):
        """启动策略"""
        if _id in self.strategyDict:
            strategy = self.strategyDict[_id]

            if strategy.inited and not strategy.trading:
                strategy.trading = True
                thread = self.getThread(self.callStrategyFunc(strategy, strategy.onStart))
                thread.start()
        else:
            self.writeCtaLog(u'策略实例不存在：%s' % _id)

    # ----------------------------------------------------------------------
    def initStrategy(self, _id):
            """初始化策略"""
            if _id in self.strategyDict:
                strategy = self.strategyDict[_id]

                if not strategy.inited:
                    strategy.inited = True
                    self.callStrategyFunc(strategy, strategy.onInit)
                else:
                    self.writeCtaLog(u'请勿重复初始化策略实例：%s' % _id)
            else:
                self.writeCtaLog(u'策略实例不存在：%s' % _id)

    # ----------------------------------------------------------------------
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
            self.writeCtaLog(u'策略实例不存在：%s' % name)

            # ----------------------------------------------------------------------

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

   # ----------------------------------------------------------------------

    def putStrategyEvent(self, name):
        """触发策略状态变化事件（通常用于通知GUI更新）"""
        event = Event(EVENT_CTA_STRATEGY + name)
        self.eventEngine.put(event)

    # ----------------------------------------------------------------------
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
            content = '\n'.join([u'策略%s触发异常已停止' % strategy.name,
                                 traceback.format_exc()])
            self.writeCtaLog(content)

    # ----------------------------------------------------------------------
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

            content = '策略%s持仓保存成功' % strategy.name
            self.writeCtaLog(content)

    # ----------------------------------------------------------------------
    def loadPosition(self):
        """从数据库载入策略的持仓情况"""
        for strategy in self.strategyDict.values():
            flt = {'name': strategy.name,
                   'vtSymbol': strategy.vtSymbol}
            posData = self.mainEngine.dbQuery(POSITION_DB_NAME, strategy.className, flt)

            for d in posData:
                strategy.pos = d['pos']

    # ----------------------------------------------------------------------
    def roundToPriceTick(self, priceTick, price):
        """取整价格到合约最小价格变动"""
        if not priceTick:
            return price

        newPrice = round(price / priceTick, 0) * priceTick
        return newPrice

        # ----------------------------------------------------------------------

    def stop(self):
        """停止"""
        pass
        # -------------------------------------------------------------------------------------------------------

    def sendOrder(self, req, strategyInstance):
        contract = self.mainEngine.getContract(req.symbol)
        vtOrderID = self.mainEngine.sendOrder(req, contract.gatewayName)  # 发单
        self.orderStrategyInstanceDict[vtOrderID] = strategyInstance  # 保存vtOrderID和策略的映射关系

        self.writeCtaLog(u'策略%s发送委托，%s，%s，%s@%s'
                         % (strategyInstance.strategyName, req.symbol, req.direction, req.volume, req.price))

        return vtOrderID

        # def sendOrder(self, vtSymbol, orderType, price, volume, strategy):

        # contract = self.mainEngine.getContract(vtSymbol)
        #
        # req = VtOrderReq()
        # req.symbol = contract.symbol
        # req.exchange = contract.exchange
        # req.price = self.roundToPriceTick(contract.priceTick, price)
        # req.volume = volume
        #
        # req.productClass = strategy.productClass
        # req.currency = strategy.currency
        #
        # # 设计为CTA引擎发出的委托只允许使用限价单
        # req.priceType = PRICETYPE_LIMITPRICE
        #
        # # CTA委托类型映射
        # if orderType == CTAORDER_BUY:
        #     req.direction = DIRECTION_LONG
        #     req.offset = OFFSET_OPEN
        #
        # elif orderType == CTAORDER_SELL:
        #     req.direction = DIRECTION_SHORT
        #
        #     # 只有上期所才要考虑平今平昨
        #     if contract.exchange != EXCHANGE_SHFE:
        #         req.offset = OFFSET_CLOSE
        #     else:
        #         # 获取持仓缓存数据
        #         posBuffer = self.posBufferDict.get(vtSymbol, None)
        #         # 如果获取持仓缓存失败，则默认平昨
        #         if not posBuffer:
        #             req.offset = OFFSET_CLOSE
        #         # 否则如果有多头今仓，则使用平今
        #         elif posBuffer.longToday:
        #             req.offset = OFFSET_CLOSETODAY
        #         # 其他情况使用平昨
        #         else:
        #             req.offset = OFFSET_CLOSE
        #
        # elif orderType == CTAORDER_SHORT:
        #     req.direction = DIRECTION_SHORT
        #     req.offset = OFFSET_OPEN
        #
        # elif orderType == CTAORDER_COVER:
        #     req.direction = DIRECTION_LONG
        #
        #     # 只有上期所才要考虑平今平昨
        #     if contract.exchange != EXCHANGE_SHFE:
        #         req.offset = OFFSET_CLOSE
        #     else:
        #         # 获取持仓缓存数据
        #         posBuffer = self.posBufferDict.get(vtSymbol, None)
        #         # 如果获取持仓缓存失败，则默认平昨
        #         if not posBuffer:
        #             req.offset = OFFSET_CLOSE
        #         # 否则如果有空头今仓，则使用平今
        #         elif posBuffer.shortToday:
        #             req.offset = OFFSET_CLOSETODAY
        #         # 其他情况使用平昨
        #         else:
        #             req.offset = OFFSET_CLOSE
        #
        # vtOrderID = self.mainEngine.sendOrder(req, contract.gatewayName)  # 发单
        # self.orderStrategyDict[vtOrderID] = strategy  # 保存vtOrderID和策略的映射关系
        #
        # self.writeCtaLog(u'策略%s发送委托，%s，%s，%s@%s'
        #                  % (strategy.name, vtSymbol, req.direction, volume, price))
        #
        # return vtOrderID

        # ----------------------------------------------------------------------

    def cancelOrder(self, vtOrderID):
        """撤单"""
        # 查询报单对象
        order = self.mainEngine.getOrder(vtOrderID)

        # 如果查询成功
        if order:
            # 检查是否报单还有效，只有有效时才发出撤单指令
            orderFinished = (order.status == constant.STATUS_ALLTRADED or order.status == constant.STATUS_CANCELLED)
            if not orderFinished:
                req = VtCancelOrderReq()
                req.symbol = order.symbol
                req.exchange = order.exchange
                req.frontID = order.frontID
                req.sessionID = order.sessionID
                req.orderID = order.orderID
                self.mainEngine.cancelOrder(req, order.gatewayName)

    # ----------------------------------------------------------------------

    def sendStopOrder(self, startegyEngine, stopOrder):
        """发停止单（本地实现）"""
        startegyEngine.stopOrderDict[stopOrder.stopOrderID] = stopOrder
        startegyEngine.workingStopOrderDict[stopOrder.stopOrderID] = stopOrder
        #
        # return stopOrderID

        # ----------------------------------------------------------------------

    def cancelStopOrder(self, strategyEngine, stopOrderID):
        """撤销停止单"""
        # 检查停止单是否存在
        if stopOrderID in strategyEngine.workingStopOrderDict:
            so = strategyEngine.workingStopOrderDict[stopOrderID]
            so.status = STOPORDER_CANCELLED
            del strategyEngine.workingStopOrderDict[stopOrderID]

    # ----------------------------------------------------------------------

    def processStopOrder(self, ticks):
        """收到行情后处理本地停止单（检查是否要立即发出）"""
        # vtSymbol = tick.vtSymbol
        #
        # # 首先检查是否有策略交易该合约
        # if vtSymbol in self.tickStrategyDict:
        #     # 遍历等待中的停止单，检查是否会被触发
        #     for so in self.workingStopOrderDict.values():
        #         if so.vtSymbol == vtSymbol:
        #             longTriggered = so.direction == DIRECTION_LONG and tick.lastPrice >= so.price  # 多头停止单被触发
        #             shortTriggered = so.direction == DIRECTION_SHORT and tick.lastPrice <= so.price  # 空头停止单被触发
        #
        #             if longTriggered or shortTriggered:
        #                 # 买入和卖出分别以涨停跌停价发单（模拟市价单）
        #                 if so.direction == DIRECTION_LONG:
        #                     price = tick.upperLimit
        #                 else:
        #                     price = tick.lowerLimit
        #
        #                 so.status = STOPORDER_TRIGGERED
        #                 self.sendOrder(so.vtSymbol, so.orderType, price, so.volume, so.strategy)
        #                 del self.workingStopOrderDict[so.stopOrderID]

        # ----------------------------------------------------------------------


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

        # ----------------------------------------------------------------------

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

        # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def insertData(self, dbName, collectionName, data):
        """插入数据到数据库（这里的data可以是VtTickData或者VtBarData）"""
        self.mainEngine.dbInsert(dbName, collectionName, data.__dict__)

    # ----------------------------------------------------------------------
    def loadBar(self, dbName, collectionName, days):
        """从数据库中读取Bar数据，startDate是datetime对象"""
        startDate = self.today - timedelta(days)

        d = {'datetime': {'$gte': startDate}}
        barData = self.mainEngine.dbQuery(dbName, collectionName, d)

        l = []
        for d in barData:
            bar = VtBarData()
            bar.__dict__ = d
            l.append(bar)
        return l

    # ----------------------------------------------------------------------
    def loadTick(self, dbName, collectionName, days):
        """从数据库中读取Tick数据，startDate是datetime对象"""
        startDate = self.today - timedelta(days)

        d = {'datetime': {'$gte': startDate}}
        tickData = self.mainEngine.dbQuery(dbName, collectionName, d)

        l = []
        for d in tickData:
            tick = VtTickData()
            tick.__dict__ = d
            l.append(tick)
        return l

        # ----------------------------------------------------------------------

    def writeCtaLog(self, content):
        """快速发出CTA模块日志事件"""
        log = VtLogData()
        log.logContent = content
        event = Event(type_=EVENT_CTA_LOG)
        event.dict_['data'] = log
        self.eventEngine.put(event)

        # ----------------------------------------------------------------------
########################################################################
class PositionBuffer(object):
    """持仓缓存信息（本地维护的持仓数据）"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.vtSymbol = constant.EMPTY_STRING

        # 多头
        self.longPosition = constant.EMPTY_INT
        self.longToday = constant.EMPTY_INT
        self.longYd = constant.EMPTY_INT

        # 空头
        self.shortPosition = constant.EMPTY_INT
        self.shortToday = constant.EMPTY_INT
        self.shortYd = constant.EMPTY_INT

    # ----------------------------------------------------------------------
    def updatePositionData(self, pos):
        """更新持仓数据"""
        if pos.direction == constant.DIRECTION_LONG:
            self.longPosition = pos.position
            self.longYd = pos.ydPosition
            self.longToday = self.longPosition - self.longYd
        else:
            self.shortPosition = pos.position
            self.shortYd = pos.ydPosition
            self.shortToday = self.shortPosition - self.shortYd

    # ----------------------------------------------------------------------
    def updateTradeData(self, trade):
        """更新成交数据"""
        if trade.direction == constant.DIRECTION_LONG:
            # 多方开仓，则对应多头的持仓和今仓增加
            if trade.offset == constant.OFFSET_OPEN:
                self.longPosition += trade.volume
                self.longToday += trade.volume
            # 多方平今，对应空头的持仓和今仓减少
            elif trade.offset == constant.OFFSET_CLOSETODAY:
                self.shortPosition -= trade.volume
                self.shortToday -= trade.volume
            # 多方平昨，对应空头的持仓和昨仓减少
            else:
                self.shortPosition -= trade.volume
                self.shortYd -= trade.volume
        else:
            # 空头和多头相同
            if trade.offset == constant.OFFSET_OPEN:
                self.shortPosition += trade.volume
                self.shortToday += trade.volume
            elif trade.offset == constant.OFFSET_CLOSETODAY:
                self.longPosition -= trade.volume
                self.longToday -= trade.volume
            else:
                self.longPosition -= trade.volume
                self.longYd -= trade.volume






