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

#region import config from easyminercenter_api_config.py
if os.path.isfile(os.curdir+os.sep+'easyminercenter_api_config.py'):
    # noinspection PyUnresolvedReferences
    from easyminercenter_api_config import *
#endregion import config from easyminercenter_api_config.py

# region config check
if (API_URL.endswith('/')):
    API_URL.rstrip('/')

r = requests.get(API_URL + '/auth?apiKey=' + API_KEY)
if (r.status_code != 200):
    print("You have to input valid API_KEY and URL of the EasyMinerCenter API endpoint!")
    quit()
# endregion config check

def write_lock(lock_file):
        with open(lock_file, 'w') as f:
            f.write("locked")

def delete_lock(lock_file):
    os.remove(lock_file)


def api_call(train,test,dataset,fold,prediction_output_file):
    print("\nprocessing " + train)
    files = {("file", open(train, 'rb'))}

    df = pd.read_csv(train)
    if "id" in dataset.keys():
        df = df.drop(dataset["id"], 1)
    # region step 1: create datasource
    headers = {"Accept": "application/json"}
    print(API_URL + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + API_KEY)
    r = requests.post(API_URL + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + API_KEY,
                      files=files, headers=headers)
    datasource_id = r.json()["id"]
    print("datasource_id:" + str(datasource_id))
    # endregion step 1: create datasource

    # region step 2: create miner
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    json_data = json.dumps(
        {"name": "test miner " + dataset["filename"], "type": "cloud", "datasourceId": datasource_id})
    r = requests.post(API_URL + "/miners?apiKey=" + API_KEY, headers=headers, data=json_data.encode())
    miner_id = r.json()["id"]
    print("miner_id:" + str(miner_id))
    # endregion step 2: create miner

    # region step 3: preprocess fields
    attributesMap = {}
    for col in df.columns:
        json_data = json.dumps(
            {"miner": miner_id, "name": col, "columnName": col, "specialPreprocessing": "eachOne"})
        print(json_data.encode())
        r = requests.post(API_URL + "/attributes?apiKey=" + API_KEY, headers=headers, data=json_data.encode())
        print("attribute creation response status code:" + str(r.status_code))
        if r.status_code != 201:
            break
        attributesMap[col] = r.json()['name']
    # endregion step 3: preprocess fields

    # region step 4: create task
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    consequent = attributesMap[dataset["targetvariablename"]]

    antecedent = []
    for col in df.columns:
        if col == consequent:
            continue
        antecedent.append({"attribute": attributesMap[col]})

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
    task_id = r.json()["id"]
    print("task_id:" + str(task_id))
    # endregion step 4: create task

    # region step 5: task run
    # start task
    r = requests.get(API_URL + "/tasks/" + str(task_id) + "/start?apiKey=" + API_KEY, headers=headers)
    if r.status_code > 400:
        print("Task creation failed. Please try to modify the task config or try it later.")
        raise

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
            print(dataset["filename"] + ": task failed executing")
            raise

    # endregion step 5: task run

    print("---proceed to evaluation---")

    # region step 6: create datasource from test
    r = requests.post(API_URL + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + API_KEY, files={("file", open(test, 'rb'))}, headers={"Accept": "application/json"})
    test_datasource_id = r.json()["id"]
    print("test datasource_id:" + str(test_datasource_id))
    time.sleep(1)
    # endregion step 6: create datasource from test

    # region step 7: evaluation
    uri = API_URL + "/evaluation/classification?scorer=easyMinerScorer&task=" + str(
        task_id) + "&datasource=" + str(test_datasource_id) + "&apiKey=" + API_KEY
    print("evaluation uri:" + uri)
    r = requests.get(uri, headers={"Accept": "application/json"})
    # endregion step 7: evaluation



    print("response status:" + str(r.status_code))

    # save classification result to prediction_file
    pred_output = open(prediction_output_file, "w")
    pred_output.write(r.text)
    pred_output.close()
#endregion

def train_and_test(output):
    #region run test tasks and evaluate partial results
    # noinspection PyUnresolvedReferences
    for dataset in datasets:
        for fold in range(0, 10):
            prediction_output_file = directory + os.sep + "results" + os.sep + dataset["filename"] + str(fold) + ".evalResult.json"
            lock_file = directory + os.sep  + dataset["filename"] + str(fold) + ".lock"
            if os.path.isfile(prediction_output_file):
                print "results for " + dataset["filename"] + " fold " + str(fold) + " already available, skipping"
                continue
            if os.path.isfile(lock_file):
                print "result for " + dataset["filename"] + " fold " + str(fold) + " being computed (locked), skipping"
                continue
            else:
                write_lock(lock_file)

            train = directory + os.sep + "folds" + os.sep + "train" + os.sep + dataset["filename"] + str(fold) + ".csv"
            test = directory + os.sep + "folds" + os.sep + "test" + os.sep + dataset["filename"] + str(fold) + ".csv"

            if not (os.path.isfile(train) and os.path.isfile(test)):
                # train or test CSV file is not available
                print("FILE ERROR: " + train)
                continue
            try:
                api_call(train,test,dataset,fold,prediction_output_file)
            except  Exception as inst:
                print inst
                print "Trying again (just once)"
                try:
                    api_call(train,test,dataset,fold,prediction_output_file)
                except  Exception as inst:
                    print inst
                    delete_lock(lock_file)
                    print "Second try failed, EXITING (lock file deleted)"
                    raise
            delete_lock(lock_file)
    #region process results CSV
    output.write("dataset;AVG rule count;test rows;true positives;false positives;uncovered;AVG accuracy;AVG of accuracies\n");

def process_results(output):
    # noinspection PyUnresolvedReferences
    for dataset in datasets:
        ruleCount = 0
        rowCount = 0
        correct = 0
        incorrect = 0
        unclassified = 0
        accuracyAvg = 0

        datasetResultsFile = directory + os.sep + "results" + os.sep + dataset["filename"] + ".summary.txt"

        for i in range(0, 10):
            jsonDataFile = open(
                directory + os.sep + "results" + os.sep + dataset["filename"] + str(i) + ".evalResult.json", "r")
            data = json.load(jsonDataFile)
            jsonDataFile.close()
            dataCorrect = int(data["correct"])
            dataRowCount = int(data["rowCount"])
            ruleCount += int(data["task"]["rulesCount"])
            rowCount += dataRowCount
            correct += dataCorrect
            incorrect += int(data["incorrect"])
            unclassified += int(data["unclassified"])
            accuracyAvg+=(dataCorrect/dataRowCount)

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

print("You can run multiple scripts in parallel to speed up processing.")
print("You can run multiple scripts in parallel to speed up processing.")
print("Answering YES will delete any lock files and compute results when the script finishes.")
master = raw_input("Is this first (master) execution?")

if master == "YES":
    files = os.listdir(directory)
    for lockfile in files:
        if lockfile.endswith(".lock"):
            os.remove(os.path.join(directory,lockfile))

resultsFile = directory + os.sep + "results" + os.sep + "_results.summary.csv"
output = open(resultsFile, "w")
train_and_test(output)
if master:
    process_results(output)
output.close()
#endregion process results CSV
