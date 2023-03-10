import json,random,string,re
from core import Instance
from UIPlugin.terminal import UIInstance

ui = UIInstance()

browserPath = '"C:\Program Files\Google\Chrome\Application\chrome.exe"'

def mainMenu(instanceList):
    print("CloudMgr V0.1.0")
    print("By Hihaar")
    print("--------------------")
    print("Select a instance")
    print("| ID | Instance Name | Instance ID |")
    for instance in range(len(instanceList)):
        printData = f"{instanceList[instance]['InstanceName']} | {instanceList[instance]['InstanceId']}"
        print(f"| {instance} | {printData} |")
    result = ''
    while result == '':
        result = input("ID> ")
    return instanceList[int(result)]
    

def selectAction(instanceInfo):
    # Read module info
    moduleListFile = open("modules.json","r")
    moduleList = json.load(moduleListFile)
    moduleListFile.close()
    instance = Instance(instanceInfo)
    instanceApi = instance.getInstanceApi()
    instanceStatus = instanceApi.getInstanceStatus()
    select = [
        f"Start {'[Unavailable]' if instanceStatus != 'Stopped' else ''}",
        f"Stop {'[Unavailable]' if instanceStatus != 'Running' else ''}",
        f"Restart {'[Unavailable]' if instanceStatus != 'Running' else ''}",
        f"Connect {'[Unavailable]' if instanceStatus != 'Running' else ''}"
    ]
    result = ui.listSelect(select,"Select a action",f"Instance {instanceInfo['InstanceName']}({instanceInfo['InstanceId']}) Selected\nInstance Status: {instanceStatus}")
    if result == '':
        return
    elif result == '1':
        startInstance(instanceApi,instanceInfo)
    elif result == '2':
        stopInstance(instanceApi, instanceInfo)
    elif result == '3':
        restartInstance(instanceApi, instanceInfo)
    elif result == '4':
        connectMenu(instanceApi, instanceInfo)

def startInstance(instanceApi,instanceInfo):
    confirm = ui.actionOverview("Start",f"{instanceInfo['InstanceName']}({instanceInfo['InstanceId']})","None")
    if confirm:
        response = instanceApi.startInstance()
        ui.message(f"Instance started. Request ID: {response.body.request_id}")

def stopInstance(instanceApi,instanceInfo):
    
    # ??????????????????, ??????????????????????????????
    stopCharging = False
    isPostPaid = False
    if instanceInfo['InstanceChargeType'] == "PostPaid":
        isPostPaid = True
    options = [
        {
            "type": "yesno",
            "question": "Force Stop?"
        }
    ]
    if isPostPaid:
        options.append({
            "type": "yesno",
            "question": "Stop Charging?"
        })
    choices = ui.options("Options",options)
    if isPostPaid:
        stopCharging = choices[1]
    options = ""
    if isPostPaid and stopCharging:
        options += "Stop Charging"
    elif isPostPaid and not stopCharging:
        options += "Keep Charging"
    elif choices[0] and isPostPaid: # ??????????????????, ?????????????????????????????????
        options += ", Force Stop"
    elif choices[0]:
        options += "Force Stop"
    else:
        options += "None"
    confirm = ui.actionOverview("Stop", f"{instanceInfo['InstanceName']}({instanceInfo['InstanceId']})", options)
    if confirm:
        response = instanceApi.stopInstance(force=choices[0], stopCharging=stopCharging)
        ui.message(f"Instance stopped. Request ID: {response.body.request_id}")


def restartInstance(instanceApi,instanceInfo):
    option = [
        {
            'type': 'yesno',
            'question': 'Force Stop?'
        }
    ]
    choice = ui.options('Options',option)
    options = ""
    if choice[0]:
        options += "Force Stop"
    else:
        options += "None"
    confirm = ui.actionOverview("Restart",instance=f"{instanceInfo['InstanceName']}({instanceInfo['InstanceId']})",options=options)
    if confirm:
        response = instanceApi.restartInstance(force=choice[0])
        ui.message(f"Instance restarted. Request ID: {response.body.request_id}")

def connectMenu(instanceApi,instanceInfo):
    menu = [
        "Connect via SSH",
        "Connect via RDP",
        "Connect Via VNC"
    ]
    choice = ui.listSelect(menu,"Connect to instance",f"Instance: {instanceInfo['InstanceName']}({instanceInfo['InstanceId']})")
    if choice == "1":
        pass
    if choice == "2":
        pass
    if choice == "3":
        connectViaVnc(instanceApi,instanceInfo)

def connectViaVnc(instanceApi,instanceInfo):
    changeVncPassword = False
    if instanceInfo['APIModuleConfig']['VNCPassword'] == "": # ???VNC??????????????????????????????????????????????????????
        changeVncPassword = True
    confirm = ui.actionOverview("Connect Via VNC",f"{instanceInfo['InstanceName']}({instanceInfo['InstanceId']})",''.join(['Change VNC Password' if changeVncPassword else 'None']))

    # ???????????????
    if confirm:
        # ??????????????????????????????????????????????????????????????????????????????getVnc
        if changeVncPassword:
            # ??????random????????????????????????
            # ????????????????????????????????????????????????????????????????????????????????????
            # while??????????????????????????????????????????????????????????????????????????????
            randomPassword = ''
            passwordNotMatchRequirements = True
            while passwordNotMatchRequirements:
                randomPassword = ''.join(random.sample(string.ascii_letters + string.digits,6))
                check = re.compile(r'[0-9a-zA-Z]{6}')
                if check.fullmatch(randomPassword) != None:
                    passwordNotMatchRequirements = False

            # VNC???????????????????????????????????????
            instanceApi.changeVncPassword(randomPassword)
            response = instanceApi.getVncUrl(vncPassword=randomPassword)
            print(f"New VNC Password: {randomPassword}\nVNC URL: {response[1]}\nRequest ID: {response[0].body.request_id}")
        else:
            response = instanceApi.getVncUrl()  # ????????????vncPassword, ??????API???????????????????????????????????????????????????????????????
            print(f"VNC URL: {response[1]}\nRequest ID: {response[0].body.request_id}")


if __name__ == "__main__":
    instancesFile = open("instances.json","r")
    instanceList = json.load(instancesFile)
    instancesFile.close()
    while True:
        print("--------------------")
        instance = mainMenu(instanceList=instanceList)
        selectAction(instance)
