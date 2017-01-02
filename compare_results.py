import os
import json

DIRECTORY_1='results'
DIRECTORY_2='results2'

for file in os.listdir(DIRECTORY_1):
    if file.endswith(".evalResult.json"):
        if not os.path.isfile(DIRECTORY_2+os.sep+file):
            print("cilovy soubor neexistuje: "+file)
            continue

        evalresult_json_1=open(DIRECTORY_1+os.sep+file).read()
        evalresult_json_1=json.loads(evalresult_json_1)

        evalresult_json_2 = open(DIRECTORY_2 + os.sep + file).read()
        evalresult_json_2 = json.loads(evalresult_json_2)

        compare_results=[]

        if evalresult_json_1['correct'] != evalresult_json_2['correct']:
            compare_results.append('correct')
        if evalresult_json_1['incorrect'] != evalresult_json_2['incorrect']:
            compare_results.append('incorrect')
        if evalresult_json_1['unclassified'] != evalresult_json_2['unclassified']:
            compare_results.append('unclassified')
        if evalresult_json_1['rowCount'] != evalresult_json_2['rowCount']:
            compare_results.append('rowCount')
        if evalresult_json_1['task']['rulesCount'] != evalresult_json_2['task']['rulesCount']:
            compare_results.append('rulesCount')

        if len(compare_results):

            print(file[0:-16]+" : "+', '.join(compare_results))