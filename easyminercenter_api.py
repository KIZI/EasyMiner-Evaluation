import requests, json
import pandas as pd
import time
import os

# import definition of datasets
from datasets import *

directory = os.getcwd()

# TODO you have to input URL of the EasyMinerCenter API endpoint and your API KEY (generated in EasyMinerCenter UI)
# you can modify the following lines, or create configuration file easyminercenter_api_config.py
API_KEY = ''
API_URL = ''

# region TASK CONFIG
AUTO_CONF_SUPP = False
USE_CBA = True
MAX_RULES_COUNT = 80000

IM_CONF = 0.5
IM_SUPP = 0.01
IM_AUTO_CONF_SUPP_MAX_RULE_LENGTH = 5
# endregion TASK CONFIG

# region import config from easyminercenter_api_config.py
if os.path.isfile(os.curdir + os.sep + 'easyminercenter_api_config.py'):
    # noinspection PyUnresolvedReferences
    from easyminercenter_api_config import *
# endregion import config from easyminercenter_api_config.py

# region config check
if (API_URL.endswith('/')):
    API_URL.rstrip('/')

r = requests.get(API_URL + '/auth?apiKey=' + API_KEY)
if (r.status_code != 200):
    print("You have to input valid API_KEY and URL of the EasyMinerCenter API endpoint!")
    quit()
# endregion config check

# region remove current result files
if os.path.isfile(directory + os.sep + "results" + os.sep + "_results.summary.csv"):
    os.remove(directory + os.sep + "results" + os.sep + "_results.summary.csv")
    print("removed file: " + "_results.summary.txt")
for dataset in datasets:
    if os.path.isfile(directory + os.sep + "results" + os.sep + dataset["filename"] + ".summary.txt"):
        os.remove(directory + os.sep + "results" + os.sep + dataset["filename"] + ".summary.txt")
        print("removed file: " + dataset["filename"] + ".summary.txt")
    for i in range(0, 10):
        if os.path.isfile(directory + os.sep + "results" + os.sep + dataset["filename"] + str(i) + ".evalResult.json"):
            os.remove(directory + os.sep + "results" + os.sep + dataset["filename"] + str(i) + ".evalResult.json")
            print("removed file: " + dataset["filename"] + str(i) + ".evalResult.json")
# endregion remove current result files

# region run test tasks and evaluate partial results
dataset_errors = []
processed_datasets_count = 0

def test_dataset (dataset, i):
    """This function runs evaluation for one dataset"""
    train = directory + os.sep + "folds" + os.sep + "train" + os.sep + dataset["filename"] + str(i) + ".csv"
    print(train)
    test = directory + os.sep + "folds" + os.sep + "test" + os.sep + dataset["filename"] + str(i) + ".csv"

    if not (os.path.isfile(train) and os.path.isfile(test)):
        # train or test CSV file is not available
        print("FILE ERROR: " + train)
        return

    print("\nprocessing " + dataset["filename"] + str(i))
    files = {("file", open(train, 'rb'))}

    df = pd.read_csv(train)
    if "id" in dataset.keys():
        df = df.drop(dataset["id"], 1)

    # region step 1: create datasource
    headers = {"Accept": "application/json"}
    print(API_URL + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + API_KEY)
    for createI in range(0, 3):
        r = requests.post(API_URL + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + API_KEY,
                          files=files, headers=headers)
        if r.status_code == 200 or r.status_code == 201:
            break
        else:
            print('--sleep [creation] -- ')
            time.sleep(10)
    if r.status_code > 201:
        raise Exception("Datasource creation failed: " + dataset["filename"] + str(i))

    datasource_id = r.json()["id"]
    print("datasource_id:" + str(datasource_id))
    if not datasource_id:
        raise Exception('Miner creation failed')
    # endregion step 1: create datasource

    # region step 2: create miner
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    json_data = {"name": "test miner " + dataset["filename"], "type": "cloud", "datasourceId": datasource_id}
    json_data = json.dumps(json_data)
    json_data = json_data.encode()
    r = requests.post(API_URL + "/miners?apiKey=" + API_KEY, headers=headers, data=json_data)
    miner_id = r.json()["id"]
    print("miner_id:" + str(miner_id))
    if not miner_id:
        raise Exception('Miner creation failed')
    # endregion step 2: create miner

    # region step 3: preprocess fields
    attributes_map = {}
    for col in df.columns:
        json_data = {"miner": miner_id, "name": col, "columnName": col, "specialPreprocessing": "eachOne"}
        json_data = json.dumps(json_data)
        json_data = json_data.encode()
        print(json_data)
        r = requests.post(API_URL + "/attributes?apiKey=" + API_KEY, headers=headers, data=json_data)
        print("attribute creation response status code:" + str(r.status_code))
        if r.status_code != 201:
            break  # TODO má to tu být?
        attributes_map[col] = r.json()['name']
    # endregion step 3: preprocess fields

    # region step 4: create task
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    consequent = attributes_map[dataset["targetvariablename"]]

    antecedent = []
    for col in df.columns:
        attribute_name = attributes_map[col]
        if attribute_name != consequent:
            antecedent.append({"attribute": attribute_name})

    task_config = {"miner": miner_id,
                   "name": "Test task", "limitHits": MAX_RULES_COUNT,
                   "IMs": [],
                   "specialIMs": [],
                   "antecedent": antecedent,
                   "consequent": [
                       {
                           "attribute": consequent
                       }
                   ]
                   }

    if AUTO_CONF_SUPP:
        task_config['IMs'].append({"name": "AUTO_CONF_SUPP"})
        task_config['IMs'].append({"name": "RULE_LENGTH", "value": IM_AUTO_CONF_SUPP_MAX_RULE_LENGTH})
    else:
        task_config['IMs'].append({"name": "CONF", "value": IM_CONF})
        task_config['IMs'].append({"name": "SUPP", "value": IM_SUPP})

    if USE_CBA:
        task_config["specialIMs"].append({"name": "CBA"})

    r = requests.post(API_URL + "/tasks/simple?apiKey=" + API_KEY, headers=headers,
                      data=json.dumps(task_config).encode())
    print("create task response code:" + str(r.status_code))
    try:
        task_id = r.json()["id"]
    except:
        raise Exception('Task creation failed')

    print("task_id:" + str(task_id))
    # endregion step 4: create task

    # region step 5: task run
    # start task
    r = requests.get(API_URL + "/tasks/" + str(task_id) + "/start?apiKey=" + API_KEY, headers=headers)
    if r.status_code > 400:
        raise Exception("Task creation failed. Please try to modify the task config or try it later.")

    # check status task
    r = requests.get(API_URL + "/tasks/" + str(task_id) + "/start?apiKey=" + API_KEY, headers=headers)

    # task_id=r.json()["id"]
    while True:
        time.sleep(1)
        # check state
        r = requests.get(API_URL + "/tasks/" + str(task_id) + "/state?apiKey=" + API_KEY, headers=headers)
        task_state = r.json()
        print("task_state:" + task_state["state"] + ", import_state:" + task_state["importState"])
        if task_state["state"] == "solved" and task_state["importState"] == "done":
            break
        if task_state["state"] == "failed" or task_state["state"] == "interrupted":
            raise Exception(dataset["filename"] + ": task failed executing")

    # endregion step 5: task run

    print("---prechod k evaluaci---")

    # region step 6: create datasource from test
    r = requests.post(API_URL + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + API_KEY,
                      files={("file", open(test, 'rb'))}, headers={"Accept": "application/json"})
    test_datasource_id = r.json()["id"]
    print("test datasource_id:" + str(test_datasource_id))
    time.sleep(5)
    # endregion step 6: create datasource from test

    # region step 7: evaluation
    uri = API_URL + "/evaluation/classification?scorer=easyMinerScorer&task=" + str(
        task_id) + "&datasource=" + str(test_datasource_id) + "&apiKey=" + API_KEY
    print("evaluation uri:" + uri)
    r = requests.get(uri, headers={"Accept": "application/json"})
    # endregion step 7: evaluation

    prediction_file = directory + os.sep + "results" + os.sep + dataset["filename"] + str(i) + ".evalResult.json"

    print("response status:" + str(r.status_code))
    rJson = r.json()
    if str(r.status_code) != "200" or not ("correct" in rJson):
        raise Exception(dataset["filename"] + ": Scorer creation or run failed.")

    # save classification result to prediction_file
    output = open(prediction_file, "w")
    rJson['test_datasource_id']=test_datasource_id
    output.write(json.dumps(rJson))
    output.close()


def slowdown_counter():
    "Function for slowdown effect (using counter processed_datasets_count)"
    global processed_datasets_count
    if processed_datasets_count > 10:
        # slowdown the evaluation script due to backend server load
        print('--slow down--')
        time.sleep(10)
        processed_datasets_count = 0
    else:
        processed_datasets_count += 1

print("--start evaluation--")

# noinspection PyUnresolvedReferences
for dataset in datasets:
    for i in range(0, 10):
        try:
            test_dataset(dataset, i)
        except Exception as e:
            dataset_errors.append({"dataset":dataset, "i":i, "error_count":0})
            print("ERROR: ")
            print(e.args)
            time.sleep(10)

        slowdown_counter()

#region rerun failed tasks
print("\n\n----\n\n")
print(dataset_errors)

while len(dataset_errors)>0:
    print("--process errors--")
    time.sleep(10)
    dataset_error = dataset_errors[0]
    dataset_error["error_count"] += 1

    if dataset_error["error_count"] >= 5:
        dataset_errors.pop(0)
        print("ERROR SKIPPED: ")
        print(dataset_error)
        continue
    try:
        print('run')
        test_dataset(dataset_error["dataset"], dataset_error["i"])
        dataset_errors.pop(0)
    except Exception as e:
        print("ERROR: ")
        print(e.args)

    slowdown_counter()
#endregion rerun failed tasks

# endregion

# region process results CSV
resultsFile = directory + os.sep + "results" + os.sep + "_results.summary.csv"
output = open(resultsFile, "w")
output.write("dataset;AVG rule count;test rows;true positives;false positives;uncovered;AVG accuracy;AVG of accuracies\n");

# noinspection PyUnresolvedReferences
for dataset in datasets:
    ruleCount = 0
    rowCount = 0
    correct = 0
    incorrect = 0
    unclassified = 0
    accuracyAvg = 0

    datasetResultsFile = directory + os.sep + "results" + os.sep + dataset["filename"] + ".summary.txt"

    process_dataset = True
    for i in range(0, 10):
        if not os.path.isfile(directory + os.sep + "results" + os.sep + dataset["filename"] + str(i) + ".evalResult.json"):
            process_dataset = False

    if (not process_dataset):
        print("SKIPPED ROW: "+dataset["filename"])
        continue

    for i in range(0, 10):
        jsonDataFile = open(directory + os.sep + "results" + os.sep + dataset["filename"] + str(i) + ".evalResult.json", "r")
        data = json.load(jsonDataFile)
        jsonDataFile.close()
        dataCorrect = int(data["correct"])
        dataRowCount = int(data["rowCount"])
        ruleCount += int(data["task"]["rulesCount"])
        rowCount += dataRowCount
        correct += dataCorrect
        incorrect += int(data["incorrect"])
        unclassified += int(data["unclassified"])
        accuracyAvg += (dataCorrect / dataRowCount)

    output.write(dataset["filename"] + ";"
                 + str(ruleCount / 10) + ";"
                 + str(rowCount) + ";"
                 + str(correct) + ";"
                 + str(incorrect) + ";"
                 + str(unclassified) + ";"
                 + str(correct / rowCount) + ";"
                 + str(accuracyAvg / 10)
                 + "\n")

    datasetOutput = open(datasetResultsFile, "w")
    datasetOutput.write("Number of rules:" + str(ruleCount) + "\n")
    datasetOutput.write("Number of test instances:" + str(rowCount) + "\n")
    datasetOutput.write("True positives:" + str(correct) + "\n")
    datasetOutput.write("False positives:" + str(incorrect) + "\n")
    datasetOutput.write("Uncovered:" + str(unclassified) + "\n\n")
    datasetOutput.write("Accuracy (total):" + str(correct / rowCount) + "\n")
    datasetOutput.write("Average of accuracies:" + str(accuracyAvg / 10) + "\n")
    datasetOutput.close()

output.close()
# endregion process results CSV
