# Solution to task 1
### Steps

1. Register the same model via cli
```
 az ml model register -n linear_regression --model-framework ScikitLearn \
  -p linear_regression.plk -g mlops_bootcamp -w mlops
 ```
2. Register the same model via Python script by using Model.register method
See documentation [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model.model?view=azure-ml-py).
```
from azureml.core.model import Model
ws = Workspace.from_config()

model = Model.register(model_path= "linear_regression.plk",
                        model_name="linear_regression", 
                        model_framework= Model.Framework.SCIKITLEARN, workspace=ws)
```
3. (Optional) Register the same model via Python script by using run.register method
See documentation [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.run.run?view=azure-ml-py#register-model-model-name--model-path-none--tags-none--properties-none--model-framework-none--model-framework-version-none--description-none--datasets-none--sample-input-dataset-none--sample-output-dataset-none--resource-configuration-none----kwargs-).
```
model = register_model(model_name = "linear_regression", 
                        model_path="linear_regression.plk",
                        model_framework="ScikitLearn")
```

## Exercise 2: Attach and remove inference cluster

### Steps

1. Attach an inference cluster via Python script
See documentation [here](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?tabs=python).
```
from azureml.core import Workspace

ws = Workspace.from_config()
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException

# Choose a name for your CPU cluster
cpu_cluster_name = "cpucluster"

# Verify that cluster does not exist already
try:
    cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    # To use a different region for the compute, add a location='<region>' parameter
    compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                           max_nodes=4)
    cpu_cluster = ComputeTarget.create(ws, cpu_cluster_name, compute_config)

cpu_cluster.wait_for_completion(show_output=True)
```
2. Remove this inference cluster via CLI
See documentation [here](https://docs.microsoft.com/en-us/cli/azure/ml(v1)/computetarget?view=azure-cli-latest#az_ml_v1__computetarget_delete).
```
az ml computetarget delete --name cpucluster \
> -g mlops_bootcamp \
> -w mlops
```
3. Optional (Remove this inference cluster via Python script)
See documentation [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.compute.computetarget?view=azure-ml-py#delete--).
```
from azureml.core.compute import ComputeTarget
from azureml.core import Workspace

ws = Workspace.from_config()

# The name of your CPU cluster to delete
cpu_cluster_name = "cpu-cluster"
cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
cpu_cluster.delete()
```

## Exercise 3: Schedule Azure Machine Learning pipeline

### Steps

1. Schedule the pipeline to run every Wednesday at 08:00 in the morning via Python Script
See documentation [here](https://docs.microsoft.com/en-us/python/api/azureml-pipeline-core/azureml.pipeline.core.schedule.schedulerecurrence?view=azure-ml-py).
``` 
from azureml.pipeline.core import ScheduleRecurrence, Schedule

weekly = ScheduleRecurrence(frequency='Week', interval=1, week_days="Wednesday",time_of_day="8:00" )

pipeline_schedule = Schedule.create(ws, name='Weekly morning Predictions',
                                        description='batch inferencing',
                                        pipeline_id=<published_pipeline.id>,
                                        experiment_name='Batch_Prediction',
                                        recurrence=weekly)
```
2. Schedule the pipeline to run every day at 13:00 via Python Script
See documentation [here](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-trigger-published-pipeline).

``` 
daily = ScheduleRecurrence(frequency='Day', interval=1, time_of_day="13:00" )
pipeline_schedule = Schedule.create(ws, name='Weekly Predictions',
                                        description='batch inferencing',
                                        pipeline_id=<published_pipeline.id from the pipeline_schedule>,
                                        experiment_name='Batch_Prediction',
                                        recurrence=daily)
```
3. Deactivate the scheduled pipeline via Python Script
See documentation [here](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-trigger-published-pipeline).
``` 
from azureml.core import Workspace
from azureml.pipeline.core import Pipeline, PublishedPipeline
from azureml.pipeline.core import Schedule

ws = Workspace.from_config()

#If the pipeline is scheduled, you must cancel the schedule first. 
#Retrieve the schedule's identifier from the portal or by running:

ss = Schedule.list(ws)
for s in ss:
    print(s)

#Once you have the schedule_id you wish to disable, run:

def stop_by_schedule_id(ws, schedule_id):
    s = next(s for s in Schedule.list(ws) if s.id == schedule_id)
    s.disable()
    return s

stop_by_schedule_id(ws, schedule_id)

pipeline = PublishedPipeline.get(ws, id=pipeline_id)
pipeline.disable()

If you then run Schedule.list(ws) again, you should get an empty list.
```
4. Optional (Explore other possible steps in the pipeline)

``` 
# It is possible to aggregate a python script step. 
# It creates an Azure ML Pipeline step that runs Python script.

from azureml.pipeline.core import PipelineData
from azureml.pipeline.steps import PythonScriptStep

# python scripts folder
prepare_data_folder = './scripts/prepdata'

# rename columns as per Azure Machine Learning NYC Taxi tutorial
green_columns = str({ 
    "vendorID": "vendor",
    "lpepPickupDatetime": "pickup_datetime",
    "lpepDropoffDatetime": "dropoff_datetime",
    "storeAndFwdFlag": "store_forward",
    "pickupLongitude": "pickup_longitude",
    "pickupLatitude": "pickup_latitude",
    "dropoffLongitude": "dropoff_longitude",
    "dropoffLatitude": "dropoff_latitude",
    "passengerCount": "passengers",
    "fareAmount": "cost",
    "tripDistance": "distance"
}).replace(",", ";")

# Define output after cleansing step
cleansed_green_data = PipelineData("cleansed_green_data", datastore=default_store).as_dataset()

print('Cleanse script is in {}.'.format(os.path.realpath(prepare_data_folder)))

# cleansing step creation
# See the cleanse.py for details about input and output
cleansingStepGreen = PythonScriptStep(
    name="Cleanse Green Taxi Data",
    script_name="cleanse.py", 
    arguments=["--useful_columns", useful_columns,
               "--columns", green_columns,
               "--output_cleanse", cleansed_green_data],
    inputs=[green_taxi_data.as_named_input('raw_data')],
    outputs=[cleansed_green_data],
    compute_target=aml_compute,
    runconfig=aml_run_config,
    source_directory=prepare_data_folder,
    allow_reuse=True
)

print("cleansingStepGreen created.")
```

It is possible to run hyperparameter tunning for Machine Learning model training.
See documentation [here](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-parameter-tuning-with-hyperdrive.ipynb).

