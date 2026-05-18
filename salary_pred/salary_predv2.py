import pandas as pd #pandas for csv handling
from sklearn.model_selection import train_test_split as tts #split the data cus uum... accuracy :)
from sklearn.linear_model import LinearRegression #my model
from sklearn.metrics import mean_absolute_error #test the error
import time as t #benchmarking

# -----------------------
# 1. Initialize everything
# -----------------------
start = t.perf_counter()
df = pd.read_csv(
    "kagglehub/datasets/nalisha/job-salary-prediction-dataset/versions/1/job_salary_prediction_dataset.csv" #ignore the path its huge ik
    ).dropna() 

drop_features = ["skills_count", "company_size", "remote_work", "location", "certifications"] #we're not using this for now
df = df.drop(columns=drop_features) #drop em

# -----------------------
# 2. Split data for training and testing
# -----------------------

x = df.drop(columns="salary") #we arent giving salary as an input, its the output!
y = df["salary"] #this going to be expected output

x_train, x_test, y_train, y_test = tts(
    x, y #give the dud the values he needs
    , test_size = 0.2 #20% test 80% train
    , random_state = 42 #makes it shuffle consistently
)

"""
-----------------------

NOTE:
experience years -> directly input cus its already numbers and its we can ordinally encode
education level -> need to map and then ordinally encode
industry -> one hot encode (get k-1 dummies)
job title -> one hot encode (get k-1 dummies)

-----------------------
"""

# -----------------------
# 3. Map out education to trainable numeric vals ordinally
# -----------------------
education_map = {
    "High School": 0,
    "Diploma": 0.5,
    "Bachelor": 1,
    "Master": 2,
    "PhD": 3
}

x_train["education_level"] = x_train["education_level"].map(education_map)
x_test["education_level"] = x_test["education_level"].map(education_map)

# -----------------------
# 4. One-hot encode industry and job title together
# -----------------------

x_train = pd.get_dummies(x_train, columns=["industry", "job_title"], drop_first = True)
x_test = pd.get_dummies(x_test, columns=["industry", "job_title"], drop_first=True)

#ALSO! make sure to reindex x_test to x_trains so we dont mess up the order when fitting and predicting! :)

x_test = x_test.reindex(columns=x_train.columns, fill_value=0)

# -----------------------
# 5. Train the model
# -----------------------

model = LinearRegression()
model.fit(x_train, y_train)
end = t.perf_counter() #end benchmark timer

# -----------------------
# 6. Predict and print mae and benchmark times
# -----------------------

pred_s = t.perf_counter()
y_pred = model.predict(x_test)
pred_e = t.perf_counter()
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: {mae}\nTraining Time: {end - start}\nPredicting Time: {pred_e - pred_s}")
