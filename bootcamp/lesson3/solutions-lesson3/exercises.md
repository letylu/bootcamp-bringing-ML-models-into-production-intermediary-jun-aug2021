---
## Exercise 1: Azurite
### Steps

1. Stop Azurite in VSC
2. Clean up Azurite in VSC
I did that at the bottom bar. I stopped in this way Azurite, azurite blob services, queue services and table services. I made the clean up procedure from the command palette.
---
## Exercise 2: Bindings
See documentation [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-expressions-patterns).
### Steps
We have to change the path defined in function.json:

1. Update bindings so that a function will be triggered by csv files only
```
"path": "predictions-input/{name}.csv"
```
2. Update bindings so that a function will be triggered by csv files, which names start with "processed-".

```
"path": "predictions-input/processed-{name}.csv"
```

---
## Exercise 3: Azure Functions App and CLI
See documentation [here](https://docs.microsoft.com/en-us/cli/azure/functionapp?view=azure-cli-latest#az_functionapp_stop).
### Steps

1. Stop Azure Functions App by using Azure CLI
az functionapp stop --name LRBlobTriggerAppp --resource-group mlops_bootcamp

2. Restart Azure Function App by using Azure CLI
```
az functionapp restart --n LRBlobTriggerAppp --g mlops_bootcamp
```

2. Remove Azure Function App by using Azure CLI
```
az functionapp delete --n LRBlobTriggerAppp --g mlops_bootcamp
```
---
## 4. Home assignment

**Goal**

Get hands-on experience with near real-time serverless inference on Azure

Follow the steps in near real-time inference on Azure
1. Create a simple Blob triggered Azure Function
- to read a file metadata, write a string "Hello World from my own deployed function!" to blob in `predictions-output`
- name it `RidgeBlobTrigger` and update bindings and Python script accordingly
- deploy it as a function app `RidgeBlobTriggerApp` at App Service Plan `MLOPSplan`
- add connection string and test it by uploading a sample.dat file to `predictions-input` container.
2. Re-use local Azurite setup to continue developing the function locally. The function has to load ridge model and write predictions to the file (blob) with the same name in `predictions-output` container.
3. Re-deploy `RidgeBlobTrigger` function to `RidgeBlobTriggerApp` with the updated bindings and function script.