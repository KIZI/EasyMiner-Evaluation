from easyminercenter.config import *
from data import datasets
from easyminercenter.lib.api import *
from random import randrange

import logging

API_URL = API_URL #TODO dynamické přiřazení adresy


datasets_list = datasets.get_all()
api = Api(API_URL)

#registrace noveho uzivatele a kontrola nastaveni pristupu
api.register_new_user()
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
                                      auto_conf_supp=False, im_conf=0.5, im_supp=0.01)
            api.run_task(task_id)

            # create test datasource and run scorer
            test_datasource_id = api.create_datasource(dataset_name, fold_id, TYPE_TEST)
            scorer_result = api.run_scorer(task_id, test_datasource_id)

        except Exception as e:
            if repeat_count>0:
                logging.exception(e)
            else:
                raise e


