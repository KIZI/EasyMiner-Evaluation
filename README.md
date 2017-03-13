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

## Integration test ("Short test")

[Short test](./easyminercenter/auto) is  a build a verification test on a set of evaluation datasets. 
Only one fold from each dataset is used and the results are not saved.
This test will fail if any of the datasets does not go through the complete classification workflow (data upload, preprocessing, classifier building, application of the classifier). This test can be considered as smoke test as it does not check whether the reported evaluation accuracy is within a certain range.


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
## Internal Benchmark ("Complex test")
The [Complex test](./easyminercenter/complex) tests writes evaluation results (accuracy, rule count) for each dataset into the `/easyminer-evaluation/results` folder.
 
 
### Default installation

```bash
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/complex/evaluation_test.py --api_url=http://easyminer-frontend/easyminercenter/api --cba --max_rules_count=80000
```

After the test has finished, you can copy test results from the stopped container to `results` folder in the current directory with
```bash
docker cp <container id>:///easyminer-evaluation/results .
```

where containedid can be retrieved with `docker ps --all`

## External Benchmark
A benchmarking suite involving also other classification algorithms is located in standalone project  [EasyMiner Bechmark](https://github.com/KIZI/EasyMiner-Benchmark). 


    
