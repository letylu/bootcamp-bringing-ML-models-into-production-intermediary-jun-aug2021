import io
import logging
import joblib
import pandas as pd
import numpy as np

import azure.functions as func
from azureml.core import  Workspace, Model

import azure.functions as func


def main(inputBlob: func.InputStream, predictions: func.Out[str]):
    logging.info("Python blob trigger function processed blob")

    #Al final, ya no se necesita y se quita de model_path y tampoco se importa, por eso lo comento
    #ws = Workspace.from_config() 

    model_path = Model.get_model_path('ridge')
    #model_path = os.path.join('..', 'models', "ridge.pkl")

    model = joblib.load(model_path)
    logging.info("model loaded")


    data = pd.read_csv(io.BytesIO(inputBlob.read()), header=None,  sep=',')
    logging.info("data loaded")

    data_array = data.to_numpy()
    logging.info("data array created")

    prediction = model.predict(data_array.reshape(1, -1))
    logging.info(" predicted values")

    result = np.array_str(prediction)
    logging.info("result")

    predictions.set(result)