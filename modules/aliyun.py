from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import json

class AliyunEcs:
    def __init__(self,instanceInfo):
        """
        Aliyun ECS Class

        Example:
        ecs = AliyunEcs(endpoint="ecs-cn-kongkong.aliyuncs.com")
        """

        self.instanceId = instanceInfo['InstanceId']
        self.instanceInfo = instanceInfo

        # 读取模块配置文件, 解析 Json 后存储到 self.moduleConfig 中
        moduleConfigFile = open("modules/config.json","r")
        self.moduleConfig = json.load(moduleConfigFile)['aliyun']
        moduleConfigFile.close()

        # 创建 Client 的 RuntimeOptions
        self.runtime = util_models.RuntimeOptions(connect_timeout=1000)

        # 读取 AccessKey 用于创建 Config 实例
        accessKeyId = self.moduleConfig['Auth']['AccessKeyId']
        accessKeySecret = self.moduleConfig['Auth']['AccessKeySecret']
        # 创建 Config 实例, 存储到 self.openApiConfig 中
        self.openApiConfig = open_api_models.Config(
            access_key_id=accessKeyId,
            access_key_secret=accessKeySecret,
            region_id=self.instanceInfo['APIModuleConfig']['RegionID']
        )

        # 通过 Config 实例创建 Ecs20140526Client
        self.ecsClient = Ecs20140526Client(config=self.openApiConfig)

    def restartInstance(self,force=False):
        # 创建重启请求
        rebootRequest = ecs_20140526_models.RebootInstanceRequest(
            instance_id=self.instanceId,
            force_stop=force
        )

        # 重启
        return self.ecsClient.reboot_instance_with_options(rebootRequest,self.runtime)

    def stopInstance(self,force=False,stopCharging=False):
        # 创建停机请求
        stopRequest = ecs_20140526_models.StopInstanceRequest(
            instance_id=self.instanceId,
            force_stop=force
        )

        # 若实例付费类型为按量付费，且 stopCharging 为 True, 则使用节省停机模式
        if stopCharging and self.instanceInfo['InstanceChargeType'] == "PostPaid":
            stopRequest.stopped_mode = "StopCharging"
        # 否则, 使用普通停机模式
        elif stopCharging == False and self.instanceInfo['InstanceChargeType'] == "PostPaid":
            stopRequest.stopped_mode = "KeepCharging"
        
        # 停机
        return self.ecsClient.stop_instance_with_options(stopRequest,self.runtime)

    def startInstance(self):
        # 创建启动请求
        startRequest = ecs_20140526_models.StartInstanceRequest(
            instance_id=self.instanceId
        )

        # 重启
        return self.ecsClient.start_instance_with_options(startRequest,self.runtime)
    
    def getInstanceStatus(self):
        getStatusRequest = ecs_20140526_models.DescribeInstanceStatusRequest(
            instance_id=[self.instanceId],
            region_id=self.instanceInfo['APIModuleConfig']['RegionID']
        )

        return self.ecsClient.describe_instance_status_with_options(getStatusRequest, self.runtime).body.instance_statuses.instance_status[0].status
    
    def getVncUrl(self, vncPassword=None):
        if vncPassword == None:
            vncPassword = self.instanceInfo['APIModuleConfig']['VNCPassword']
        getVncUrlRequest = ecs_20140526_models.DescribeInstanceVncUrlRequest(
            region_id=self.instanceInfo['APIModuleConfig']['RegionID'],
            instance_id=self.instanceId
        )
        response = self.ecsClient.describe_instance_vnc_url_with_options(getVncUrlRequest, self.runtime)
        return [response,f"https://g.alicdn.com/aliyun/ecs-console-vnc2/0.0.8/index.html?"
            f"vncUrl={response.body.vnc_url}&"
            f"instanceId={self.instanceId}&"
            f"isWindows={'true' if self.instanceInfo['APIModuleConfig']['IsWindows'] else 'false'}"
            f"&password={vncPassword}"]

    def changeVncPassword(self,newVncPassword):
        # 检查是否允许修改VNC密码
        if self.moduleConfig['VNC']['AllowVNCPasswordChange'] == False:
            raise PermissionError("Changing VNC Password is not allowed in module config.")
        else:
            changeVncPasswordRequest = ecs_20140526_models.ModifyInstanceVncPasswdRequest(
                region_id=self.instanceInfo['APIModuleConfig']['RegionID'],
                vnc_password=newVncPassword,
                instance_id=self.instanceId
            )
            response = self.ecsClient.modify_instance_vnc_passwd_with_options(changeVncPasswordRequest, self.runtime)
            return response


def getApiClass():
    return AliyunEcs
        
        
