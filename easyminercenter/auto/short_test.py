from data import datasets
from easyminercenter.lib.api import *
from random import randrange
import logging
import sys
import getopt

API_URL = ''
API_KEY = ''
USE_AUTO_CONF_SUPP = False

#region params
try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["auto_conf_supp", "api_key=", "api_url="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    sys.exit(2)

for option, value in opts:
    if option == "--auto_conf_supp":
        if value=="" or value==1:
            USE_AUTO_CONF_SUPP = True
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
    fold_id = randrange(0, 9, 1)
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

            #zde je možné logovat výsledky

            logging.info('TEST FINISHED SUCCESFULLY: ' + dataset_name + str(fold_id))
            break
        except Exception as e:
            if repeat_count>0:
                logging.exception(e)
            else:
                raise e


