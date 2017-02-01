import logging
import os
import requests
import json
import time
from data.datasets import *


class Api:
    api_key = ''
    api_url = ''

    def __init__(self, api_url : str, api_key : str  = ''):
        if api_url.endswith(os.sep):
            self.api_url=api_url.rstrip(os.sep)
        else:
            self.api_url = api_url
        self.api_key = api_key

    def register_new_user(self):
        """
        Funkce pro registraci nového uživatele
        """
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        testname='testuser' + str(time.time())
        user_data = { 'name': testname, 'email': testname + '@domain.tld', 'password': testname}

        r = requests.post(self.api_url + '/users?apiKey=' + self.api_key, headers = headers, data = json.dumps(user_data).encode())
        if r.status_code == 201:
            json_data = r.json()
            self.api_key = json_data['apiKey']
            time.sleep(5)
            logging.info('Registered user: ' + str(json_data['id']))
        else:
            logging.error('User creation failed: ' + r.text)
            raise Exception('User creation failed.')

    def check_user_access(self):
        """
        Funkce pro kontrolu pristupnosti API pomoci zadane URL a API klice
        """
        r = requests.get(self.api_url + '/auth?apiKey=' + self.api_key)
        if r.status_code == 200:
            logging.info('API check: ' + self.api_url + '/auth?apiKey=' + self.api_key)
        else:
            logging.error('Invalid URL or API KEY!', [self.api_url, self.api_key])
            raise Exception('Invalid URL or API KEY!', [self.api_url, self.api_key])

    def create_datasource(self, dataset_name : str, dataset_fold : int, dataset_type : str):
        """
        Funkce pro vytvoření nového datasource (STEP 1)
        :param dataset_name: str
        :param dataset_fold: int
        :param dataset_type: str
        :return: int
        """
        file = get_filename(dataset_name, dataset_fold, dataset_type)
        if not os.path.isfile(file):
            logging.error('File not exists: ' + file)
            raise Exception("Dataset file not found: " + file)
        files = {("file", open(file, 'rb'))}
        datasource_id = -1
        headers = {"Accept": "application/json"}

        for createI in range(0, 3):
            r = requests.post(self.api_url + '/datasources?separator=%2C&encoding=utf8&type=limited&apiKey=' + self.api_key,
                              files=files, headers=headers)
            if r.status_code == 200 or r.status_code == 201:
                datasource_id = r.json()["id"]
                if datasource_id:
                    logging.info("Dataset created (dataset_name + " " + str(dataset_fold) + " " + dataset_type): " + str(datasource_id))
                    return datasource_id
            else:
                if createI >= 2:
                    raise Exception("Datasource creation failed: " + dataset_name + " " + str(dataset_fold) + " " + dataset_type)
                else:
                    logging.info('Dataset creation failed, repeat it: ' + dataset_name + " " + str(dataset_fold) + " " + dataset_type)
                    time.sleep(10)

        raise Exception('Miner creation failed')

    def create_miner(self, datasource_id : int, miner_name: str = "test miner"):
        """
        Funkce pro vytvoreni mineru z existujiciho datasource (STEP 2)
        :param datasource_id: - str
        :param miner_name: str - jmeno mineru
        :return: str - ID mineru
        """
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        json_data = {"name": miner_name + str(time.time()) , "type": "cloud", "datasourceId": datasource_id}
        json_data = json.dumps(json_data).encode()
        r = requests.post(self.api_url + "/miners?apiKey=" + self.api_key, headers=headers, data=json_data)
        miner_id = r.json()["id"]
        logging.info('Miner created: '+str(miner_id))
        if not miner_id:
            raise Exception('Miner creation failed.')
        else:
            return miner_id

    def preprocess_fields_each_one(self, miner_id : int):
        attributes_map = {}
        headers = {"Accept": "application/json"}
        r = requests.get(self.api_url + '/miners/' + str(miner_id) + '?apiKey=' + self.api_key, headers = headers)
        if r.status_code != 200:
            raise Exception("Requested miner not found: " + str(miner_id))
        datasource_id = r.json()['datasourceId']

        r = requests.get(self.api_url + '/datasources/' + str(datasource_id) +  '?apiKey=' + self.api_key, headers = headers)
        if r.status_code != 200:
            raise Exception("Datasource for miner " + str(miner_id) + " not found: " + str(datasource_id))

        datasource_data = r.json()
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        for column in datasource_data['column']:
            #zpracujeme jednotlive sloupce
            json_data = {'miner':miner_id, 'name': column['name'], 'columnName': column['name'], 'specialPreprocessing': 'eachOne'}
            json_data = json.dumps(json_data).encode()

            r = requests.post(self.api_url + '/attributes?apiKey=' + self.api_key, headers = headers, data = json_data)
            logging.info('attribute creation: ' + column['name'] + ' - ' + str(r.status_code))
            if r.status_code != 201:
                print(r.text)
                raise Exception("Attribute creation failed: miner_id=" + str(miner_id) + ", column=" + column['name'] + ', status=' + str(r.status_code))
            attributes_map[column['name']] = r.json()['name']

        return attributes_map

    def create_task(self, miner_id : int, attributes_map, target_column_name : str, max_rules_count : int = 80000, use_cba : bool = True, auto_conf_supp : bool = False, im_auto_conf_supp_max_rule_length : int = 5, im_conf : float = 0.5, im_supp : float = 0.01 ):
        """
        Funkce pro vytvoreni jednoduche data miningove ulohy na zaklade vstupnich parametru
        :param miner_id:
        :param attributes_map:
        :param target_column_name:
        :param max_rules_count:
        :param use_cba:
        :param auto_conf_supp:
        :param im_auto_conf_supp_max_rule_length:
        :param im_conf:
        :param im_supp:
        :return:
        """
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        consequent = attributes_map[target_column_name]

        antecedent = []
        for column_name in attributes_map:
            attribute_name = attributes_map[column_name]
            if attribute_name != consequent:
                antecedent.append({"attribute": attribute_name})

        task_config = {"miner": miner_id,
                       "name": "Test task", "limitHits": max_rules_count,
                       "IMs": [],
                       "specialIMs": [],
                       "antecedent": antecedent,
                       "consequent": [
                           {
                               "attribute": consequent
                           }
                       ]
                       }


        if auto_conf_supp:
            task_config['IMs'].append({"name": "AUTO_CONF_SUPP"})
            task_config['IMs'].append({"name": "RULE_LENGTH", "value": im_auto_conf_supp_max_rule_length})
        else:
            task_config['IMs'].append({"name": "CONF", "value": im_conf})
            task_config['IMs'].append({"name": "SUPP", "value": im_supp})

        if use_cba:
            task_config["specialIMs"].append({"name": "CBA"})

        r = requests.post(self.api_url + "/tasks/simple?apiKey=" + self.api_key, headers=headers, data=json.dumps(task_config).encode())
        logging.info("create task response code:" + str(r.status_code))
        try:
            task_id = r.json()["id"]
            return task_id
        except:
            raise Exception('Task creation failed')

    def run_task(self, task_id : str):
        """
        Funkce pro vypocitani data-mininingove ulohy (STEP 5)
        :param task_id: str - ID jiz vytvorene ulohy
        """
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        r = requests.get(self.api_url + "/tasks/" + str(task_id) + "/start?apiKey=" + self.api_key, headers=headers)
        if r.status_code > 400:
            raise Exception("Task creation failed. Please try to modify the task config or try it later.")

        # check status task
        r = requests.get(self.api_url + "/tasks/" + str(task_id) + "/start?apiKey=" + self.api_key, headers=headers)

        while True:
            time.sleep(1)
            # check state
            r = requests.get(self.api_url + "/tasks/" + str(task_id) + "/state?apiKey=" + self.api_key, headers=headers)
            task_state = r.json()
            logging.info("task " + str(task_id) + " --- state: " + task_state["state"] + ", import_state:" + task_state["importState"])
            if task_state["state"] == "solved" and task_state["importState"] == "done":
                logging.info('Task solved: ' + str(task_id))
                break
            if task_state["state"] == "failed" or task_state["state"] == "interrupted":
                raise Exception("Task run failed: " + str(task_id))

    def run_scorer(self, task_id : str, test_datasource_id : str):
        """
        Funkce pro spuštění scoreru
        :param task_id:
        :param test_datasource_id:
        :return:
        """
        uri = self.api_url + "/evaluation/classification?scorer=easyMinerScorer&task=" + str(task_id) + "&datasource=" + str(test_datasource_id) + "&apiKey=" + self.api_key
        logging.info("evaluation uri:" + uri)
        r = requests.get(uri, headers={"Accept": "application/json"})
        return r.json()