# EasyMiner-Evaluation

This repository contains evaluation/benchmarking datasets and scripts for [EasyMiner project](http://easyminer.eu).
    
## Setup
Code  for preparing evaluation on the same docker server where data mining services of [EasyMiner](http://github.com/kizi/easyminer) are running.

```bash
docker build -t easyminer-evaluation https://github.com/kizi/easyminer-evaluation.git#master
```
### Interactive mode
In order to manually run the python evaluation script, you need to login to the Docker container:

```bash
docker run --name easyminer-evaluation -it --network easyminer easyminer-evaluation /bin/bash
```

## Integration test ("short test")

[Short test](./easyminercenter/auto) is  a build a verification test on a set of evaluation datasets. This test will fail if any of the datasets does not go through the complete classification workflow (data upload, preprocessing, classifier building, application of the classifier). This test can be considered as smoke test as it does not check whether the reported evaluation accuracy is within a certain range.


### Default installation
If you  use the default docker image names defined in the repository [kizi/EasyMiner](https://github.com/KIZI/EasyMiner), the run command is:

```bash
# Run of evaluation test using EasyMiner server installed using docker images
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://easyminer-frontend/easyminercenter/api 
```

### Default installation with custom parameters
CBA enabled and max_rules_count redefined to 80.000.

```bash
# Run of evaluation test using EasyMiner server installed using docker images
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://easyminer-frontend/easyminercenter/api --cba --max_rules_count=80000
```

More information on the [parameters](./easyminercenter/complex).

### Custom HTTP_SERVER_ADDR 
```bash
# HEADS UP: docker-server base URL or public IP of the easyminer frontend  
HTTP_SERVER_ADDR=<docker-server>
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://$HTTP_SERVER_ADDR/easyminercenter/api
```     
## Benchmark ("Evaluation test")
The [Evaluation test](./easyminercenter/complex) tests writes evaluation results (accuracy, rule count) for each dataset into the `/easyminer-evaluation/results` folder.
 
### Default installation

```bash
# Default run of base integration test of EasyMiner server installed using docker images 
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/complex/evaluation_test.py --api_url=http://easyminer-frontend/easyminercenter/api
```

## Dependencies

The evaluation datasets were created using [marcbench](https://github.com/kliegr/marcbench)  with discretization.


    
