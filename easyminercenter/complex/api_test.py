from data import datasets
from easyminercenter.lib.api import *
from random import randrange
import logging
import sys
import getopt

API_URL = ''
API_KEY = ''
USE_AUTO_CONF_SUPP = False
USE_CBA = False
MAX_RULES_COUNT = 80000
MIN_CONFIDENCE = 0.5
MIN_SUPPORT = 0.01
MAX_RULE_LENGTH = 0

#region params
try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["auto_conf_supp", "cba", "min_conf=", "min_supp=", "max_rule_length=", "max_rules_count=", "api_key=", "api_url="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    sys.exit(2)

for option, value in opts:
    if option == "--auto_conf_supp":
        if value == "" or value == 1 or value == "=1":
            USE_AUTO_CONF_SUPP = True
    elif option == "--cba":
        if value == "" or value == 1 or value == "=1":
            USE_CBA = True
    elif option == "--min_conf":
        if not value.isdigit():
            raise "Param min_conf has to have numeric value from interval [0;1]"
        value = float(value)
        if float(value) > 1 or float(value) < 1:
            raise "Param min_conf has to have numeric value from interval [0;1]"
        MIN_CONFIDENCE = value
    elif option == "--min_supp":
        if not value.isdigit():
            raise "Param min_supp has to have numeric value from interval [0;1]"
        value = float(value)
        if  value > 1 or value < 1:
            raise "Param min_supp has to have numeric value from interval [0;1]"
        MIN_SUPPORT = value
    elif option == "--max_rule_length":
        if not value.isdigit():
            raise "Param max_rule_length has to have integer value 0 or higher than 2"
        try:
            value = int(value)
        except:
            raise "Param max_rule_length has to have integer value 0 or higher than 2"
        if value>0 and value<2:
            raise "Param max_rule_length has to have integer value 0 or higher than 2"
        MAX_RULE_LENGTH= value
    elif option == "--max_rules_count":
        if not value.isdigit():
            raise "Param max_rules_count has to have integer value higher than 0"
        try:
            value = int(value)
        except:
            raise "Param max_rules_count has to have integer value higher than 0"
        if  value<1:
            raise "Param max_rules_count has to have integer value higher than 0"
        MAX_RULES_COUNT=value
    elif option == "--api_key":
        API_KEY=value
    elif option == "--api_url":
        API_URL=value
#endregion params


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

datasets_list = datasets.get_all()

if API_KEY:
    api = Api(API_URL, API_KEY)
else:
    api = Api(API_URL)
    #registrace noveho uzivatele
    api.register_new_user()

#kontrola nastaveni pristupu
api.check_user_access()

for dataset in datasets_list:
    #FIXME
    if RANDOM_FOLDS:
        fold_id = randrange(0, 9, 1)
    else:
        fold_id = 1
    dataset_name = dataset['name']
    target_variable = dataset['target_variable']

    repeat_count = 3

    while repeat_count>0:
        repeat_count -= 1
        try:
            # create dataset and miner
            datasource_id = api.create_datasource(dataset_name, fold_id, TYPE_TRAIN)
            miner_id = api.create_miner(datasource_id, dataset_name + str(fold_id))

            # preprocess attributes
            attributes_map = api.preprocess_fields_each_one(miner_id)

            # create and run task
            task_id = api.create_task(miner_id=miner_id, attributes_map=attributes_map, max_rules_count=80000,
                                      use_cba=True,
                                      auto_conf_supp=USE_AUTO_CONF_SUPP, im_conf=0.5, im_supp=0.01, target_column_name=dataset['target_variable'])
            api.run_task(task_id)

            # create test datasource and run scorer
            test_datasource_id = api.create_datasource(dataset_name, fold_id, TYPE_TEST)
            scorer_result = api.run_scorer(task_id, test_datasource_id)

            # kontrola toho, zda nejsou vraceny jen nulove hodnoty
            if int(scorer_result["correct"]) > 0 and int(scorer_result["rowCount"]) > 0:
                logging.info("Accuracy: " + str(int(scorer_result["correct"])/int(scorer_result["rowCount"])))
            else:
                raise Exception("Invalid scorer values, or accuracy is null!")

            #zde je mozne logovat vysledky

            logging.info('TEST FINISHED SUCCESFULLY: ' + dataset_name + str(fold_id))
            break
        except Exception as e:
            if repeat_count>0:
                logging.exception(e)
            else:
                raise e


