# coding:utf-8
import json
import requests
import configparser
import warnings


warnings.filterwarnings("ignore")
config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

# СФЕРА параметры
devUser = config["SFERAUSER"]["devUser"]
devPassword = config["SFERAUSER"]["devPassword"]
sferaUrlLogin = config["SFERA"]["sferaUrlLogin"]
sferaUrlSearch = config["SFERA"]["sferaUrlSearch"]
sferaUrl = config["SFERA"]["sferaUrl"]

session = requests.Session()
session.post(sferaUrlLogin, json={"username": devUser, "password": devPassword}, verify=False)

def getTaskQuery(query):
    urlQuery = sferaUrlSearch + "?query=" + query
    response = session.get(urlQuery, verify=False)
    return json.loads(response.text)


def taskSetStatusClosed(taskId):
    data = {
        "customFieldsValues": [
            {
                "code": "resolution",
                "value": "Готово"
            }
        ],
        "resolution": [
            "Готово"
        ],
        "status": "closed"
    }
    url = sferaUrl + taskId
    session.patch(url, json=data, verify=False)


def taskSetStatus(taskId, status):
    data = {"status": status}
    url = sferaUrl + taskId
    session.patch(url, json=data, verify=False)


def taskSetSpent(taskId, spent):
    data = \
        {
            "spent": spent,
            "description": "",
            "userLogin": devUser,
            "propertiesToRemove": ["remainder"]
        }
    url = sferaUrl + taskId
    session.patch(url, json=data, verify=False)


def closeAllTaskInSprint(tempCount):
    count = tempCount+1
    print("Закрыть:")
    query = "statusCategory+!%3D+%27Done%27+and+area+%3D+%27SKOKR%27+and+hasActiveSprint()+and+type+in+(%27task%27)+and+status%3D%27inProgress%27"
    queryResult = getTaskQuery(query)
    for task in queryResult['content']:
        count = count - 1
        if count == 0:
            return
        taskId = task['number']
        print(taskId)
        taskSetStatusClosed(taskId)

    count = tempCount+1
    print("В работу:")
    query = "statusCategory+!%3D+%27Done%27+and+area+%3D+%27SKOKR%27+and+hasActiveSprint()+and+type+in+(%27task%27)+and+status%3D%27created%27"
    queryResult = getTaskQuery(query)
    for task in queryResult['content']:
        count = count - 1
        if count == 0:
            return
        taskId = task['number']
        print(taskId)
        taskSetStatus(taskId, "inProgress")
        spend = task['estimation']
        taskSetSpent(taskId, spend)


def changeSubTaskSprintDueDate(oldSprint, newSprint, date):
    query = "statusCategory+!%3D+%27Done%27+and+area+%3D+%27SKOKR%27+and+type+in+(%27subtask%27)+and+not+hasOnlyActiveOrPlannedSprint()+and+sprint%3D%27" + oldSprint + "%27"
    #query = "statusCategory+!%3D+%27Done%27+and+area+%3D+%27SKOKR%27+and+type+in+(%27subtask%27)+and+sprint%3D%27" + oldSprint + "%27"
    urlQuery = sferaUrlSearch + "?query=" + query
    #urlQuery = sferaUrl + "?query=" + query
    #urlQuery = "https://sfera.inno.local/app/tasks/api/v1/entity-views?page=0&size=20&attributes=checkbox%2Cnumber%2Cname%2Cpriority%2Cstatus%2Cassignee%2Cowner%2CdueDate%2Clabel%2Ccomponent%2CactualSprint%2Cdecision%2Cresolution%2CnameProject%2CarchTaskReason%2CexternalLinks%2Cattachments%2Csystems%2CsubSystems%2CstreamConsumer%2CstreamOwner%2CprojectConsumer%2CaffectedInVersion%2CfixedInVersion%2C%20rank%2C%20id%2C%20parent%2C%20worklog%2C%20type%2C%20serviceClass%2C%20estimation&query=area%3D%27SKOKR%27%20and%20statusCategory%21%3D%27Done%27%20and%20type%20in%20%28%27subtask%27%29%20and%20sprint%20%3D%20%274259%27"
    data = {
        "sprint": newSprint,
        "dueDate": date
    }
    response = session.get(urlQuery, verify=False)
    subTasks = json.loads(response.text)
    for subTask in subTasks['content']:
        subTaskNumber = subTask['number']
        print(subTaskNumber)
        url = sferaUrl + subTaskNumber
        session.patch(url, json=data, verify=False)


# Ежедневное закрытие задач. цифра внутри скобок = количеству взятых в работу и закрываемых задач
closeAllTaskInSprint(5)

# Перенос подзадач с одного спринта на следующий
# (только во время того, когда закрыт один спринт, но еще не открыт другой = среда).
# date - Дата испонения, которая будет проставлена в подзадачах
#changeSubTaskSprintDueDate(oldSprint='4335', newSprint='4336', date="2025-03-26")