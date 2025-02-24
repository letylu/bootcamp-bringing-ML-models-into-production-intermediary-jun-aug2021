# MIT License
# Copyright (c) Microsoft Corporation. All rights reserved.
# This script is adapted from Francesca Lazzeri Energy Demand Forecast Workbench workshop.
# Copyright (c) 2021 PyLadies Amsterdam, Alyona Galyeva

import os
import pickle
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from azureml.core import Workspace, Dataset
from azureml.core.experiment import Experiment

model_name = sys.argv[1]

WORKDIR = os.getcwd()

# set forecast horizon
H = 6

def generate_forecasts(test_df):
    '''
    The models trained are 'one-step' forecasts
    because they are trained to predict one time period into the
    future. Here, we use the trained model recursively to predict
    multiple future time steps. At each iteration from time t+1
    to the forecast horizon H, the predictions from the previous
    steps become the lagged demand input features for subsequent
    predictions.
    '''

    predictions_df = test_df.copy()
    X_test = test_df.copy().drop(['demand', 'timeStamp'], axis=1)

    # Iterate over future time steps
    for n in range(1, H+1):
        predictions_df['pred_t+'+str(n)] = model.predict(X_test)

        # shift lagged demand features...
        shift_demand_features(X_test)

        # ...and replace demand_lag1 with latest prediction
        X_test['demand_lag1'] = predictions_df['pred_t+'+str(n)]

    return predictions_df


def shift_demand_features(df):
    for i in range(H, 1, -1):
        df['demand_lag'+str(i)] = df['demand_lag'+str(i-1)]


def evaluate_forecast(predictions_df, n):
    '''
    Compute forecast performance metrics for every n step ahead
    '''

    y_true = predictions_df['demand']
    y_pred = predictions_df['pred_t+'+str(n)]
    error = y_pred - y_true

    metrics = {}

    # forecast bias
    metrics['ME'] = error.mean()
    metrics['MPE'] = 100 * (error / y_true).mean()

    # forecast error
    #MSE = mean_squared_error(y_true, y_pred)
    metrics['MSE'] = (error**2).mean()
    metrics['RMSE'] = metrics['MSE']**0.5
    metrics['MAPE'] = 100 * (error.abs() / y_true).mean()
    metrics['sMAPE'] = 200 * (error.abs() / y_true).mean()

    # relative error
    naive_pred = predictions_df['demand_lag'+str(n)]
    naive_error = naive_pred - y_true
    RE = error / naive_error
    metrics['MAPE_base'] = 100 * (naive_error.abs() / y_true).mean()
    metrics['MdRAE'] = np.median(RE.abs())

    return metrics


def plot_metric(metric, performance_metrics):
    '''
    Plots metrics over forecast period t+1 to t+H
    '''
    plt_series = performance_metrics.stack()[metric]
    fig = plt.figure(figsize=(6, 4), dpi=75)
    plt.plot(plt_series.index, plt_series)
    plt.xlabel("Forecast t+n")
    plt.ylabel(metric)
    fig.savefig(os.path.join('.', 'outputs', metric + '.png'), bbox_inches='tight')


if __name__=='__main__':
    ws = Workspace.from_config()

    test_ds = Dataset.get_by_name(ws, name="test_nyc_demand_data")
    test = test_ds.to_pandas_dataframe()

    eval_experiment = Experiment(ws, name="Evaluation_ridge")
    run = eval_experiment.start_logging()
    run.log("dataset name", test_ds.name)
    run.log("dataset version", test_ds.version)

   # Load trained model pipeline
    with open(os.path.join(WORKDIR, model_name + '.pkl'), 'rb') as f:
        model = pickle.load(f)
    run.log("model name", model_name)

    # generate forecasts on the test set
    predictions_df = generate_forecasts(test)

    # calculate model performance metrics
    performance_metrics = pd.DataFrame.from_dict({1:evaluate_forecast(predictions_df, 1),
                                                2:evaluate_forecast(predictions_df, 2),
                                                3:evaluate_forecast(predictions_df, 3),
                                                4:evaluate_forecast(predictions_df, 4),
                                                5:evaluate_forecast(predictions_df, 5),
                                                6:evaluate_forecast(predictions_df, 6)})

    # Compute and log average of metrics over the forecast horizon
    horizon_mean = performance_metrics.mean(axis=1)
    for metric, value in horizon_mean.iteritems():
        run.log(metric + '_horizon', value)

    # Log the t+1 forecast metrics
    for metric, value in performance_metrics[1].iteritems():
        run.log(metric, value)

    # Plot metrics over forecast period. View the output in Run History to view.
    plot_metric('MAPE', performance_metrics)
    plot_metric('MdRAE', performance_metrics)
    plot_metric('MPE', performance_metrics)

    # Output the predictions dataframe
    with open(os.path.join(WORKDIR, model_name + '_predictions.pkl'), 'wb') as f:
        pickle.dump(predictions_df, f)

    # Store the trained model in the Outputs folder.
    with open(os.path.join('.', 'outputs', model_name + '.pkl'), 'wb') as f:
        pickle.dump(model, f)

    run.complete()