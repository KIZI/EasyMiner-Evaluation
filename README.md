# EasyMiner-Evaluation

This repository contains prepared evaluation datasets and evaluation scripts for [EasyMiner project](http://easyminer.eu).
    
## Run using docker
Example code in case you want to run evaluation on the same docker server as data mining services of [EasyMiner](http://github.com/kizi/easyminer).

```bash
docker build -t easyminer-evaluation https://github.com/kizi/easyminer-evaluation.git#master
```
### Run bash the docker container interactive
...for access to the evaluation results, manual run of python scripts etc.:
```bash
docker run --name easyminer-evaluation -it --network easyminer easyminer-evaluation /bin/bash
```


### Simple state test
For EasyMiner state test, and then run the container using command (with replacement of the URL part): 
```bash
# HEADS UP: docker-server base URL or public IP of the easyminer frontend  
HTTP_SERVER_ADDR=<docker-server>
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://$HTTP_SERVER_ADDR/easyminercenter/api
```     

If you have used the default docker image names defined in the repository [kizi/EasyMiner](https://github.com/KIZI/EasyMiner), the run command is:
```bash
# Default run of simple test of EasyMiner server installed using docker images 
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/complex/evaluation_test.py --api_url=http://easyminer-frontend/easyminercenter/api
```

### Evaluation test run using docker
```bash
# Run of evaluation test using EasyMiner server installed using docker images
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://easyminer-frontend/easyminercenter/api --cba --max_rules_count=80000
```

## List of available tests
* [Short test](./easyminercenter/auto) - short, simple test of EasyMiner server
* [Evaluation test](./easyminercenter/complex) - evaluation testing of EasyMiner with results generated into output folder 
    