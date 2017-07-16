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
from vnpy.trader.app.ctaStrategy.ctaTemplate import *
from vnpy.trader.app.strategy.strategyEngine import *



########################################################################
class CtaEngine(StrategyEngine):
    """CTA策略引擎"""


    #----------------------------------------------------------------------
    def __init__(self, mainEngine, eventEngine):
        """Constructor"""
        super(CtaEngine,self).__init__(mainEngine,eventEngine)
        self.strategyThreadNum = 0

    #----------------------------------------------------------------------
    def putStrategyEvent(self, name):
        """触发策略状态变化事件（通常用于通知GUI更新）"""
        event = Event(EVENT_CTA_STRATEGY+name)
        self.eventEngine.put(event)
        
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

    # ----------------------------------------------------------------------
    def buildOrder(self, symbol, orderType, price, volume,contract):
            #生成委托单
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
                        req.offset = constant.OFFSET_CLOSETODAY
                    # 其他情况使用平昨
                    else:
                        req.offset = constant.OFFSET_CLOSE

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
                        req.offset = constant.OFFSET_CLOSETODAY
                    # 其他情况使用平昨
                    else:
                        req.offset = constant.OFFSET_CLOSE

            return req


    # ----------------------------------------------------------------------
    def buildStopOrder(self, symbol, orderType, price, volume):
            """生成停止单（本地实现）"""
            self.stopOrderCount += 1
            stopOrderID = STOPORDERPREFIX + str(self.stopOrderCount)

            so = StopOrder()
            so.vtSymbol = symbol
            so.orderType = orderType
            so.price = price
            so.volume = volume
            #so.strategy = strategyInstance
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

            return so


    def buildCancelOrder(self, order):
                """生成撤单"""
                req = VtCancelOrderReq()
                req.symbol = order.symbol
                req.exchange = order.exchange
                req.frontID = order.frontID
                req.sessionID = order.sessionID
                req.orderID = order.orderID
                return req
        
    
    


