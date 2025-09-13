### create enviroment from scratch

``` bash
conda create -n agents python=3.11
conda activate agents
conda install -c conda-forge poetry 
conda env export --from-history > enviroment.yml
```
run agent:
langgraph dev 

run api:
fastapi dev app/api.py