
from vnpy.trader.vtGlobal import globalDict


class CommonUtils(object):

    def __init__(self):
        super(CommonUtils, self).__init__()


    def dictValue(self,dictClass,dictValue):
        dictItem = {}
        dictItem = globalDict[dictClass]
        return dictItem[dictValue]
