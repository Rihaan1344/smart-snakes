import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error as mae_calc
from sklearn.model_selection import train_test_split as tts
import matplotlib.pyplot as plt

df = pd.read_csv(
    "kagglehub/datasets/nalisha/job-salary-prediction-dataset/versions/1/job_salary_prediction_dataset.csv" 
    #ignore the path its huge ik
).dropna()
