import os.path

TYPE_TRAIN = 'train'
TYPE_TEST = 'test'
DATASETS = [
    {"name": "anneal", "target_variable": "class"},
    {"name": "australian", "target_variable": "Y"},
    {"name": "heart-h", "target_variable": "num"},
    {"name": "heart-statlog", "target_variable": "class"},
    {"name": "kr-vs-kp", "target_variable": "class"},
    {"name": "heart-c", "target_variable": "num"},
    {"name": "pima", "target_variable": "class"},
    {"name": "tic-tac-toe", "target_variable": "Class"},
    {"name": "audiology", "target_variable": "class"},
    {"name": "balance-scale", "target_variable": "class"},
    {"name": "car", "target_variable": "class"},
    {"name": "breast-cancer", "target_variable": "class"},
    {"name": "house-votes-84", "target_variable": "class"},
    {"name": "primary-tumor", "target_variable": "class"},
    {"name": "soybean", "target_variable": "class"},
    {"name": "splice", "target_variable": "Class"},
    {"name": "mushroom", "target_variable": "class"},
    {"name": "vote", "target_variable": "Class"},
    {"name": "zoo", "target_variable": "class"},
    {"name": "autos", "target_variable": "XClass"},
    {"name": "breast-w", "target_variable": "Class"},
    {"name": "colic", "target_variable": "surgical_lesion"},
    {"name": "credit-a", "target_variable": "class"},
    {"name": "credit-g", "target_variable": "class"},
    {"name": "diabetes", "target_variable": "class"},
    {"name": "glass", "target_variable": "Type"},
    {"name": "hepatitis", "target_variable": "Class"},
    {"name": "hypothyroid", "target_variable": "Class"},
    {"name": "ionosphere", "target_variable": "class"},
    {"name": "iris", "target_variable": "class"},
    {"name": "labor", "target_variable": "class"},
    {"name": "letter", "target_variable": "class"},
    {"name": "lymph", "target_variable": "class"},
    {"name": "sick", "target_variable": "Class"},
    {"name": "sonar", "target_variable": "Class"},
    {"name": "vehicle", "target_variable": "Class"},
    {"name": "segment", "target_variable": "class"},
    {"name": "spambase", "target_variable": "class"},
    {"name": "vowel", "target_variable": "Class"},
    {"name": "waveform-5000", "target_variable": "class"}
]

def get_all():
    datasets = DATASETS
    return datasets
    #return datasets.sort(key=lambda x: x['name'].lower())

def get_filename(name: str, fold: int, type: str):
    """ Function returning filename of the file with required dataset
    :param name: str
    :param fold: int from 0 to 9
    :param type: str 'test' or 'train'
    :return: str
    """
    if type != TYPE_TRAIN and type != TYPE_TEST:
        raise "Invalid dataset type: " + type
    directory = os.path.dirname(os.path.realpath(__file__))
    if directory.endswith(os.sep):
        directory.rstrip(os.sep)
    return directory + os.sep + type + os.sep + name + str(fold) + ".csv"
