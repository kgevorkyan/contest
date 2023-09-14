# Repository for [Global Software Analysis Competition](https://gsac.tech/)

This project automatically tests and compares all participants' static analysis tools.

* To participate in this contest, users should develop a software analyzer using the
  provided [template](./example-analyzer)
* They should accept the [assignment](https://classroom.github.com/a/S_09sdh2) and submit as a
  github repository which will be visible only to admins

### To get all the requirements run the following script

```shell
sudo /path/to/contest/install_required_packages.sh
```

## Usage

* To run this tool and get corresponding rates on our test suites
  users must set the following environment variable as an argument
    * TOOLS_LIST - path to a simple text file where is written repository urls of static analyzers

* Use [run_evaluate.sh](/run_evaluate.sh) script for running tool.
    * This script will iterate over all given repositories, run each tool on tests and check results

## Results
* A special result directory will be created after running `result_dir_%Y_%m_%d_%H_%M_%S`
* In that directory you can find 
  * all tools with their results `tool_dir/result_sarif_files`
  * the evaluated scores on test suite in JSON and XML formatted files
