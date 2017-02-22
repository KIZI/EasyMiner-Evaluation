#evaluation_test.py

## Params

* **--auto_conf_supp** - use automatic configuration of confidence and support
* **--cba** - use CBA prunning 
* **--min_conf=** - value of required minimal confidence (unusable in conjunction with --auto_conf_supp; default value = 0.5)
* **--min_supp=** - value of reguired minimal support (unusable in conjunction with --auto_conf_supp; default value = 0.01)
* **--max_rule_length=** max count of attributes in individual association rule (optional)
* **--max_rules_count=** max association rules count (optional, default value is 10000)
* **--api_key=** - existing API key (optional)
* **--api_url=** - EasyMiner API endpoint URL
* **--output=** - configuration of folder for results (optional)
* **--continue** - optional, the script should continue after the previous, unfinished run

## Recommended combinations of params
Run with default confidence (0.5) and support (0.01), CBA prunning and max rules count 80000: 
```
evaluation_test.py --api_url=http://easyminer-frontend/easyminercenter/api --cba --max_rules_count=80000
```

Run with auto configuration of confidence and support, with CBA prunning and max rules count 80000:
```
evaluation_test.py --api_url=http://easyminer-frontend/easyminercenter/api --auto-conf-supp --cba --max_rules_count=80000
```