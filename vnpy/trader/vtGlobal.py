# encoding: UTF-8

"""
通过VT_setting.json加载全局配置
"""

import os
import traceback
import json


globalSetting = {}      # 全局配置字典
globalDict = {}   #全局业务字典
settingFileName = "VT_setting.json"
dictFileName = "dict.json"
path = os.path.abspath(os.path.dirname(__file__)) 
settingFileName = os.path.join(path, settingFileName)
dictFileName = os.path.join(path,dictFileName)
try:
    f = file(settingFileName)
    globalSetting = json.load(f)

    d = file(dictFileName)
    globalDict = json.load(d)
except:
    traceback.print_exc()
    
