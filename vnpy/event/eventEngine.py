# encoding: UTF-8

# 系统模块
from Queue import Queue, Empty
from collections import defaultdict
from random import *
from threading import Thread

# 第三方模块
from qtpy.QtCore import QTimer
from vnpy.trader.vtEvent import *
# 自己开发的模块
from eventType import *


########################################################################
class EventEngine(object):
    """
    事件驱动引擎
    事件驱动引擎中所有的变量都设置为了私有，这是为了防止不小心
    从外部修改了这些变量的值或状态，导致bug。
    
    变量说明
    __queue：私有变量，事件队列
    __active：私有变量，事件引擎开关
    __thread：私有变量，事件处理线程
    __timer：私有变量，计时器
    __handlers：私有变量，事件处理函数字典
    
    
    方法说明
    __run: 私有方法，事件处理线程连续运行用
    __process: 私有方法，处理事件，调用注册在引擎中的监听函数
    __onTimer：私有方法，计时器固定事件间隔触发后，向事件队列中存入计时器事件
    start: 公共方法，启动引擎
    stop：公共方法，停止引擎
    register：公共方法，向引擎中注册监听函数
    unregister：公共方法，向引擎中注销监听函数
    put：公共方法，向事件队列中存入新的事件
    
    事件监听函数必须定义为输入参数仅为一个event对象，即：
    
    函数
    def func(event)
        ...
    
    对象方法
    def method(self, event)
        ...
        
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """初始化事件引擎"""
        # 系统消息/信息事件队列
        self.__msg_queue = Queue()

        # 交易回报事件队列
        self.__trade_queue = Queue()

        #tick数据相关
        #tick数据事件字典，每个合约对应一个queue
        self.__tick_queue_dict = {}
        #每个时刻所有跟踪的的tick的快照
        self.__tick_snapshot = {}


        #策略盯的合约的行情数据的相关数据结构
        #字典{strategyInstance Id:{tick:[111,333],bat:[222,999]}}
        self.__strategy_market_dict = {}

        #策略的交易回报事件队列字典
        #字典{strategyInstance Id:strategyInstance.tradeEventQueue}
        self.__strategy_trade_queue_dict = {}




        #一个线程池数组，生成多个线程来分组处理注册的策略实例的tick数据
        self.__tick_sorter_threads = []
        self.__sorter_size = 3
        #一个策略实例分组的数组
        self.__sorter_group_list = []




        
        # 事件引擎开关
        self.__active = False
        # 事件处理线程
        self.__tickProcess_thread = Thread(target = self.__tickProcess_run)
        self.__tradeProcess_thread = Thread(target = self.__tradeProcess_run)
        self.__msgPorcess_thread = Thread(target = self.__msgProcess_run)
        # 计时器，用于触发计时器事件
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__onTimer)
        
        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.__handlers = defaultdict(list)
        
        # __generalHandlers是一个列表，用来保存通用回调函数（所有事件均调用）
        self.__generalHandlers = []

        for i in range(self.__sorter_size):
             self.__tick_sorter_threads.append(Thread(target=self.sorter_run))
             #self.__strategy_group_list.append(list())
        self.__tickProcess_thread.start()
        self.__tradeProcess_thread.start()
        self.__msgPorcess_thread.start()
    #----------------------------------------------------------------------
    def __tickProcess_run(self):
        #启动tick事件分拣线程
        for sorter in self.__tick_sorter_threads:
              sorter.start()

        while self.__active == True:
            try:
                self.tick_snapshot();
            except Empty:
                pass
    #--------------------------------------------------------------------------
    def __tradeProcess_run(self):
        # 启动交易相关的回报线程
        while self.__active == True:
            try:
                 #将交易回报队列中的事件分发到不同的策略实例所持有的交易回报队列中
                 pass
            except Empty:
                pass

    # --------------------------------------------------------------------------
    def __msgProcess_run(self):
        #启动通用线程
        while self.__active == True:
            try:
                event = self.__msg_queue.get(block = True, timeout = 1)  # 获取事件的阻塞时间设为1秒
                self.__process(event)
            except Empty:
                pass
    #----------------------------------------------------------------------
    def sorter_run(self):
        #tick按策略进行分拣
        pass
    #----------------------------------------------------------------------
    def tick_snapshot(self):
        #取出tick队列中的数据赋值到tick快照中
        for key in self.__tick_queue_dict:
            self.__tick_snapshot[key] = self.__tick_queue_dict[key].get(block = True,timeout=1)

    def __process(self, event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.__handlers[event.type_]]
            
            # 以上语句为Python列表解析方式的写法，对应的常规循环写法为：
            #for handler in self.__handlers[event.type_]:
                #handler(event) 
        
        # 调用通用处理函数进行处理
        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]
               
    #----------------------------------------------------------------------
    def __onTimer(self):
        """向事件队列中存入计时器事件"""
        # 创建计时器事件
        event = Event(type_=EVENT_TIMER)
        
        # 向队列中存入计时器事件
        self.put(event)    

    #----------------------------------------------------------------------
    def start(self, timer=True):
        """
        引擎启动
        timer：是否要启动计时器
        """
        # 将引擎设为启动
        self.__active = True

        
        # 启动计时器，计时器事件间隔默认设定为1秒
        if timer:
            self.__timer.start(1000)
    
    #----------------------------------------------------------------------
    def stop(self):
        """停止引擎"""
        # 将引擎设为停止
        self.__active = False
        
        # 停止计时器
        self.__timer.stop()

            
    #----------------------------------------------------------------------
    def register(self, type_, handler):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无defaultDict会自动创建新的list
        handlerList = self.__handlers[type_]
        
        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)
            
    #----------------------------------------------------------------------
    def unregister(self, type_, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求   
        handlerList = self.__handlers[type_]
            
        # 如果该函数存在于列表中，则移除
        if handler in handlerList:
            handlerList.remove(handler)

        # 如果函数列表为空，则从引擎中移除该事件类型
        if not handlerList:
            del self.__handlers[type_]
            
    # #----------------------------------------------------------------------
    def put(self,event,type=MSG_TYPE):
         if type == TICK_TYPE:
             self.__tick_queue_dict[event.dict_['id']].put(event)
         elif type == TRADE_TYPE:
             self.__trade_queue.put(event)
         else :
             self.__msg_queue.put(event)
    #----------------------------------------------------------------------

    def QueueInit(self,symbol,type):
        """tick事件数组初始化，在向gateWay调用行情订阅的时候，需要调用此方法"""
        if type == 'tick':
         if  self.__tick_queue_dict[symbol] is None:
              self.__tick_queue_dict[symbol] = Queue()

    #----------------------------------------------------------------------
    def strategyListener(self,strategy):
      """各个策略实例加入行情事件监听"""
      if strategy.market['ticks'] is not None:
            self.strategyTickListener(self,strategy)
      if strategy.market['bars'] is not None:
            self.strategyBarListener(self, strategy)
      if self.__strategy_market_dict[strategy._id] is None:
        self.__strategy_market_dict[strategy._id] = {};
      self.__sorter_group_list[random.randint(0,self.__sorter_size)].append(strategy._id)
      self.__strategy_trade_queue_dict[strategy._id] = strategy.tradeEventQueue

    #----------------------------------------------------------------------
    def strategyTickListener(self,strategy):
        for tick in strategy.market['ticks']:
             if self.__strategy_market_dict[strategy._id]['tick'] is None:
                 self.__strategy_market_dict[strategy._id]['tick'] = []
             self.__strategy_market_dict[strategy._id]['tick'].append(tick.symbol)
             if self.__tick_queue_dict[tick.symbol] is None:
                self.__tick_queue_dict[tick.symbol] = Queue()

    #----------------------------------------------------------------------
    def strategyBarListener(self,strategy):
        pass


    #----------------------------------------------------------------------
    def registerGeneralHandler(self, handler):
        """注册通用事件处理函数监听"""
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)
            
    #----------------------------------------------------------------------
    def unregisterGeneralHandler(self, handler):
        """注销通用事件处理函数监听"""
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)
        


########################################################################
# class EventEngine2(object):
#     """
#     计时器使用python线程的事件驱动引擎
#     """
#
#     #----------------------------------------------------------------------
#     def __init__(self):
#         """初始化事件引擎"""
#         # 事件队列
#         self.__queue = Queue()
#
#         # 事件引擎开关
#         self.__active = False
#
#         # 事件处理线程
#         self.__thread = Thread(target = self.__run)
#
#         # 计时器，用于触发计时器事件
#         self.__timer = Thread(target = self.__runTimer)
#         self.__timerActive = False                      # 计时器工作状态
#         self.__timerSleep = 1                           # 计时器触发间隔（默认1秒）
#
#         # 这里的__handlers是一个字典，用来保存对应的事件调用关系
#         # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
#         self.__handlers = defaultdict(list)
#
#         # __generalHandlers是一个列表，用来保存通用回调函数（所有事件均调用）
#         self.__generalHandlers = []
#
#     #----------------------------------------------------------------------
#     def __run(self):
#         """引擎运行"""
#         while self.__active == True:
#             try:
#                 event = self.__queue.get(block = True, timeout = 1)  # 获取事件的阻塞时间设为1秒
#                 self.__process(event)
#             except Empty:
#                 pass
#
#     #----------------------------------------------------------------------
#     def __process(self, event):
#         """处理事件"""
#         # 检查是否存在对该事件进行监听的处理函数
#         if event.type_ in self.__handlers:
#             # 若存在，则按顺序将事件传递给处理函数执行
#             [handler(event) for handler in self.__handlers[event.type_]]
#
#             # 以上语句为Python列表解析方式的写法，对应的常规循环写法为：
#             #for handler in self.__handlers[event.type_]:
#                 #handler(event)
#
#         # 调用通用处理函数进行处理
#         if self.__generalHandlers:
#             [handler(event) for handler in self.__generalHandlers]
#
#     #----------------------------------------------------------------------
#     def __runTimer(self):
#         """运行在计时器线程中的循环函数"""
#         while self.__timerActive:
#             # 创建计时器事件
#             event = Event(type_=EVENT_TIMER)
#
#             # 向队列中存入计时器事件
#             self.put(event)
#
#             # 等待
#             sleep(self.__timerSleep)
#
#     #----------------------------------------------------------------------
#     def start(self, timer=True):
#         """
#         引擎启动
#         timer：是否要启动计时器
#         """
#         # 将引擎设为启动
#         self.__active = True
#
#         # 启动事件处理线程
#         self.__thread.start()
#
#         # 启动计时器，计时器事件间隔默认设定为1秒
#         if timer:
#             self.__timerActive = True
#             self.__timer.start()
#
#     #----------------------------------------------------------------------
#     def stop(self):
#         """停止引擎"""
#         # 将引擎设为停止
#         self.__active = False
#
#         # 停止计时器
#         self.__timerActive = False
#         self.__timer.join()
#
#         # 等待事件处理线程退出
#         self.__thread.join()
#
#     #----------------------------------------------------------------------
#     def register(self, type_, handler):
#         """注册事件处理函数监听"""
#         # 尝试获取该事件类型对应的处理函数列表，若无defaultDict会自动创建新的list
#         handlerList = self.__handlers[type_]
#
#         # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
#         if handler not in handlerList:
#             handlerList.append(handler)
#
#     #----------------------------------------------------------------------
#     def unregister(self, type_, handler):
#         """注销事件处理函数监听"""
#         # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
#         handlerList = self.__handlers[type_]
#
#         # 如果该函数存在于列表中，则移除
#         if handler in handlerList:
#             handlerList.remove(handler)
#
#         # 如果函数列表为空，则从引擎中移除该事件类型
#         if not handlerList:
#             del self.__handlers[type_]
#
#     #----------------------------------------------------------------------
#     def put(self, event):
#         """向事件队列中存入事件"""
#         self.__queue.put(event)
#
#     #----------------------------------------------------------------------
#     def registerGeneralHandler(self, handler):
#         """注册通用事件处理函数监听"""
#         if handler not in self.__generalHandlers:
#             self.__generalHandlers.append(handler)
#
#     #----------------------------------------------------------------------
#     def unregisterGeneralHandler(self, handler):
#         """注销通用事件处理函数监听"""
#         if handler in self.__generalHandlers:
#             self.__generalHandlers.remove(handler)
#
#
# ########################################################################
class Event:
    """事件对象"""

    #----------------------------------------------------------------------
    def __init__(self, type_=None):
        """Constructor"""
        self.type_ = type_      # 事件类型
        self.dict_ = {}         # 字典用于保存具体的事件数据


#----------------------------------------------------------------------
# def test():
#     """测试函数"""
#     import sys
#     from datetime import datetime
#     from PyQt4.QtCore import QCoreApplication
#
#     def simpletest(event):
#         print u'处理每秒触发的计时器事件：%s' % str(datetime.now())
#
#     app = QCoreApplication(sys.argv)
#
#     ee = EventEngine2()
#     #ee.register(EVENT_TIMER, simpletest)
#     ee.registerGeneralHandler(simpletest)
#     ee.start()
#
#     app.exec_()


# # 直接运行脚本可以进行测试
# if __name__ == '__main__':
#     test()