# Basic Import
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge,Lasso,ElasticNet
from sklearn.tree import DecisionTreeRegressor
from src.exception import CustomException
from src.logger import logging

from src.utils import save_object
from src.utils import evaluate_model

from dataclasses import dataclass
import sys
import os
import json

@dataclass 
class ModelTrainerConfig:
    trained_model_file_path: str
    model_report_file_path: str


class ModelTrainer:
    def __init__(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        artifacts_dir = os.path.join(project_root, 'artifacts')
        self.model_trainer_config = ModelTrainerConfig(
            trained_model_file_path=os.path.join(artifacts_dir, 'model.pkl'),
            model_report_file_path=os.path.join(artifacts_dir, 'model_report.json')
        )

    def initate_model_training(self,train_array,test_array):
        try:
            logging.info('Splitting Dependent and Independent variables from train and test data')
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            models = {
                'LinearRegression': LinearRegression(),
                'Lasso': Lasso(),
                'Ridge': Ridge(),
                'Elasticnet': ElasticNet(),
                'DecisionTree': DecisionTreeRegressor()
            }

            model_report: dict = evaluate_model(X_train, y_train, X_test, y_test, models)
            print(model_report)
            print('\n====================================================================================\n')
            logging.info(f'Model Report : {model_report}')

            # To get best model score from dictionary
            best_model_score = max(sorted(model_report.values()))

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            best_model = models[best_model_name]

            print(f'Best Model Found , Model Name : {best_model_name} , R2 Score : {best_model_score}')
            print('\n====================================================================================\n')
            logging.info(f'Best Model Found , Model Name : {best_model_name} , R2 Score : {best_model_score}')

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            # Save all model accuracies for frontend display.
            os.makedirs(os.path.dirname(self.model_trainer_config.model_report_file_path), exist_ok=True)
            with open(self.model_trainer_config.model_report_file_path, 'w') as report_file:
                json.dump(model_report, report_file, indent=4)

        except Exception as e:
            logging.info('Exception occured at Model Training')
            raise CustomException(e, sys)