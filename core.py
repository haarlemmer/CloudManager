import json
from importlib import import_module

class Instance:
    def __init__(self, instanceInfo):
        self.instanceInfo = instanceInfo
        # 读取模块列表, 初始化 API 模块
        moduleListFile = open("modules.json","r")
        self.moduleList = json.load(moduleListFile)
        moduleListFile.close()

    def getInstanceApi(self):
        # 读取模块信息并引用模块
        self.moduleInfo = self.moduleList[self.instanceInfo['APIModuleId']]
        
        mod = import_module(f"modules.{self.moduleInfo['APIFile']}").getApiClass()
        
        # 创建实例(这里指的不是创建一台服务器)
        return mod(self.instanceInfo)

