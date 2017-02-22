from data import datasets
from easyminercenter.lib.api import *
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

RESULTS_DIRECTORY = ""
CONTINUE_PREVIOUS_RUN = False

# region params
try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["auto_conf_supp", "cba", "min_conf=", "min_supp=", "max_rule_length=", "max_rules_count=", "api_key=", "api_url=", "output=", "continue"])
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
    elif option == "--continue":
        if value == "" or value == 1 or value == "=1":
            CONTINUE_PREVIOUS_RUN = True
    elif option == "--min_conf":
        if not value.isdigit():
            raise Exception("Param min_conf has to have numeric value from interval [0;1]")
        value = float(value)
        if float(value) > 1 or float(value) < 1:
            raise Exception("Param min_conf has to have numeric value from interval [0;1]")
        MIN_CONFIDENCE = value
    elif option == "--min_supp":
        if not value.isdigit():
            raise Exception("Param min_supp has to have numeric value from interval [0;1]")
        value = float(value)
        if  value > 1 or value < 1:
            raise Exception("Param min_supp has to have numeric value from interval [0;1]")
        MIN_SUPPORT = value
    elif option == "--max_rule_length":
        if not value.isdigit():
            raise Exception("Param max_rule_length has to have integer value 0 or higher than 2")
        try:
            value = int(value)
        except:
            raise Exception("Param max_rule_length has to have integer value 0 or higher than 2")
        if value>0 and value<2:
            raise Exception("Param max_rule_length has to have integer value 0 or higher than 2")
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
    elif option == "--output":
        RESULTS_DIRECTORY=value
# endregion params

# region check if results directory is writable
if RESULTS_DIRECTORY == "":
    # vychozi adresar pro vysledky
    RESULTS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    if not RESULTS_DIRECTORY.endswith(os.sep):
        RESULTS_DIRECTORY += os.sep
    RESULTS_DIRECTORY += ".." + os.sep + ".." + os.sep + "results"

if RESULTS_DIRECTORY.endswith(os.sep):
    # odstraneni lomitka z konce cesty k adresari s vysledky
    RESULTS_DIRECTORY.rstrip(os.sep)

if not os.path.isdir(RESULTS_DIRECTORY):
    raise Exception("Results directory does not exist: " + RESULTS_DIRECTORY)

logging.info("RESULTS DIRECTORY: " + os.path.realpath(RESULTS_DIRECTORY))
# endregion check if results directory is writable

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


def slowdown_counter():
    """
    Function for slowdown effect (using counter processed_datasets_count)
    :return:
    """
    global processed_datasets_count
    if processed_datasets_count > 10:
        # slowdown the evaluation script due to backend server load
        logging.info('--slow down--')
        time.sleep(10)
        processed_datasets_count = 0
    else:
        processed_datasets_count += 1


def get_results_filename(dataset_name: str, fold_id: int = -1, file_type: str = ".evalResult.json") -> str:
    """
    Funkce vracejici jmeno souboru pro ulozeni vysledku klasifikace
    :param dataset_name:str
    :param fold_id:int
    :param file_type: str
    :return: str
    """
    result = RESULTS_DIRECTORY + os.sep + dataset_name
    if fold_id >= 0:
        result += "_" + str(fold_id)
    result += file_type
    return result


# region remove current result files
if not CONTINUE_PREVIOUS_RUN:
    for dataset in datasets_list:
        dataset_name = dataset['name']
        for fold_id in range(0, 10):
            fold_results_filename = get_results_filename(dataset_name, fold_id)
            if os.path.isfile(fold_results_filename):
                os.remove(fold_results_filename)
                logging.info("removed file: "+os.path.basename(fold_results_filename))

    results_csv_filename=get_results_filename(dataset_name="_results", file_type=".summary.csv")
    if os.path.isfile(results_csv_filename):
        os.remove(results_csv_filename)
        logging.info("removed file: " + os.path.basename(results_csv_filename))

    results_json_filename = get_results_filename(dataset_name="_results", file_type=".summary.json")
    if os.path.isfile(results_json_filename):
        os.remove(results_json_filename)
        logging.info("removed file: " + os.path.basename(results_json_filename))

# endregion remove current result files

# region test jednotlivych datasetu
processed_datasets_count=0
for dataset in datasets_list:
    for fold_id in range(0, 10):
        dataset_name = dataset['name']
        target_variable = dataset['target_variable']

        # kontrola, jestli nemame pokracovat v prechozim vyhodnoceni vysledku
        if CONTINUE_PREVIOUS_RUN and os.path.isfile(get_results_filename(dataset_name, fold_id)):
            # jiz existuje soubor s vysledky, preskocime tento beh
            logging.info("SKIPPING: " + dataset_name + " " + fold_id)
            continue

        # maximalni pocet opakovani
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
                task_id = api.create_task(miner_id=miner_id, attributes_map=attributes_map, max_rules_count=MAX_RULES_COUNT,
                                          use_cba=USE_CBA, auto_conf_supp=USE_AUTO_CONF_SUPP, max_rule_length=MAX_RULE_LENGTH,
                                          im_conf=0.5, im_supp=0.01, target_column_name=dataset['target_variable'])
                api.run_task(task_id)

                # create test datasource and run scorer
                test_datasource_id = api.create_datasource(dataset_name, fold_id, TYPE_TEST)
                scorer_result = api.run_scorer(task_id, test_datasource_id)

                # kontrola toho, zda nejsou vraceny jen nulove hodnoty
                if not (int(scorer_result["rowCount"]) > 0):
                    raise Exception("Invalid scorer values, or accuracy is null!")

                # ulozeni vysledku klasifikace do pracovniho souboru
                output_file = open(get_results_filename(dataset_name, fold_id), "w")
                output_file.write(json.dumps(scorer_result))
                output_file.close()

                slowdown_counter()

                break
            except Exception as e:
                if repeat_count>0:
                    # slow down
                    logging.exception(e)
                    time.sleep(30)
                else:
                    raise e
# endregion test jednotlivych datasetu

# region zpracovani vysledku
output_csv_file=open(get_results_filename(dataset_name="_results",file_type=".summary.csv"),"w")
output_results = {}

for dataset in datasets_list:
    rule_count = 0
    row_count = 0
    correct = 0
    incorrect = 0
    unclassified = 0
    accuracy_avg = 0
    dataset_name = dataset['name']

    # region kontrola, jestli existuji foldy za cely dataset
    process_dataset = True
    for fold_id in range(0, 10):
        if not os.path.isfile(get_results_filename(dataset_name, fold_id)):
            process_dataset = False

    if (not process_dataset):
        logging.error('Dataset skipped [not all results available]: ' + dataset_name)
        continue
    # endregion kontrola, jestli existuji foldy za cely dataset

    for fold_id in range(0, 10):
        fold_results_file = open(get_results_filename(dataset_name, fold_id), "r")
        fold_results = json.load(fold_results_file)
        fold_results_file.close()

        fold_results_data_correct = int(fold_results["correct"])
        fold_results_data_row_count = int(fold_results["rowCount"])
        rule_count += int(fold_results["task"]["rulesCount"])
        row_count += fold_results_data_row_count
        correct += fold_results_data_correct
        incorrect += int(fold_results["incorrect"])
        unclassified += int(fold_results["unclassified"])
        accuracy_avg += (fold_results_data_correct / fold_results_data_row_count)

    output_csv_file.write(dataset_name + ";"
                 + str(rule_count / 10) + ";"
                 + str(row_count) + ";"
                 + str(correct) + ";"
                 + str(incorrect) + ";"
                 + str(unclassified) + ";"
                 + str(correct / row_count) + ";"
                 + str(accuracy_avg / 10)
                 + "\n")


    output_results[dataset_name] = {
        "rule_count": rule_count,
        "row_count": row_count,
        "correct": correct,
        "incorrect": incorrect,
        "unclassified": unclassified,
        "accuracy": str(correct / row_count),
        "avg_of_accuracies": str(accuracy_avg / 10)
    }

output_csv_file.close()
output_json_file = open(get_results_filename(dataset_name="_results",file_type=".summary.json"), "w")
output_json_file.write(json.dumps(output_results))
output_json_file.close()

logging.info('EVALUATION FINISHED')
# endregion zpracovani vysledku
