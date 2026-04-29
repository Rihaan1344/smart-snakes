import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import time as t

drop_features = ["skills_count", "company_size", "remote_work", "location", "certifications"]

# -----------------------
# 1. Load data
# -----------------------

start = t.perf_counter()
df = pd.read_csv(
    "kagglehub/datasets/nalisha/job-salary-prediction-dataset/versions/1/job_salary_prediction_dataset.csv"
).dropna()
df = df.drop(columns=drop_features)

# -----------------------
# 2. Split 
# -----------------------
X = df.drop(columns=["salary"])
y = df["salary"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# -----------------------
# 3. One-hot encode industry
# -----------------------
X_train = pd.get_dummies(X_train, columns=["industry"], drop_first=True)
X_test = pd.get_dummies(X_test, columns=["industry"], drop_first=True)

# Align test columns with train columns
X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

# -----------------------
# 4. Education encoding (ordinal)
# -----------------------
edu_map = {
    "High School": 0,
    "Diploma": 0.5,
    "Bachelor": 1,
    "Master": 2,
    "PhD": 3
}

"""

edu levels

PhD            163976.005295
Master         153305.307833
Bachelor       142410.531291
Diploma        137158.574976
High School    131715.336243
"""

X_train["education_level_encoded"] = X_train["education_level"].map(edu_map)
X_test["education_level_encoded"] = X_test["education_level"].map(edu_map)

# -----------------------
# 5. Mean encoding job_title (ONLY from train)
# -----------------------
mean_job = X_train.join(y_train).groupby("job_title")["salary"].mean()

X_train["job_title_encoded"] = X_train["job_title"].map(mean_job)
X_test["job_title_encoded"] = X_test["job_title"].map(mean_job)

# Fill unseen job titles in test
X_test["job_title_encoded"] = X_test["job_title_encoded"].fillna(y_train.mean())

# -----------------------
# 6. Drop original categorical columns
# -----------------------
X_train = X_train.drop(columns=["job_title", "education_level"])
X_test = X_test.drop(columns=["job_title", "education_level"])

# -----------------------
# 7. Train model
# -----------------------
model = LinearRegression()
model.fit(X_train, y_train)

end = t.perf_counter()

# -----------------------
# 8. Predict + evaluate
# -----------------------
pred_s = t.perf_counter()
y_pred = model.predict(X_test)
pred_e = t.perf_counter()

mae = mean_absolute_error(y_test, y_pred)
print("MAE:", mae)
print("Training Time: ", end - start)
print("Predicting Time: ", pred_e - pred_s)