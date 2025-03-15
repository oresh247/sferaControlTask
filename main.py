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


closeAllTaskInSprint(5)