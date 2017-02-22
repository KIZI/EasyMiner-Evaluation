import requests, json, os

API_KEY = 'h4c2JX18040ylgb7YJrUwV8cwF85742ydyccTrHcZO61nUqz0rx'
DATA_API_URL = 'http://xtest.lmcloud.vse.cz/easyminer-data/api/v1'
PREPROCESSING_API_URL = 'http://xtest.lmcloud.vse.cz/easyminer-preprocessing/api/v1'

# region import config from easyminercenter_api_config.py
if os.path.isfile(os.curdir + os.sep + 'easyminercenter_api_config.py'):
    # noinspection PyUnresolvedReferences
    from easyminercenter_api_config import *
# endregion import config from easyminercenter_api_config.py

datasources = requests.get(DATA_API_URL+'/datasource?apiKey='+API_KEY,headers={"Accept": "application/json"}).json()
for datasource in datasources:
    r = requests.delete(DATA_API_URL+'/datasource/'+str(datasource['id'])+'?apiKey='+API_KEY)
    if(r.status_code==200):
        print('DELETED: ' + DATA_API_URL + '/datasource/' + str(datasource['id']))
    else:
        print('delete FAILED: ' + DATA_API_URL + '/datasource/' + str(datasource['id']))


datasets = requests.get(PREPROCESSING_API_URL+'/dataset?apiKey='+API_KEY,headers={"Accept": "application/json"}).json()
for dataset in datasets:
    r = requests.delete(PREPROCESSING_API_URL+'/dataset/'+str(dataset['id'])+'?apiKey='+API_KEY)
    if(r.status_code==200):
        print('DELETED: ' + PREPROCESSING_API_URL + '/dataset/' + str(dataset['id']))
    else:
        print('delete FAILED: ' + PREPROCESSING_API_URL + '/dataset/' + str(dataset['id']))

print('--DONE--')