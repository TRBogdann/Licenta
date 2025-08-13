
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix,accuracy_score
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# df = pd.read_csv('./dataIN/ckd_fill/mice.csv')
df = pd.read_csv('./dataIN/ckd_fill/knn.csv',index_col=0)

models_name = [
    "RANDOM_FOREST",
    "XGBOOST",
    "LOGISTIC",
]

X_train,X_test,y_train,y_test = train_test_split(df.drop(columns=['classification']),df['classification'],random_state=42,train_size=0.7)

models = [
    RandomForestClassifier(max_depth=5),
    XGBClassifier(),
    LogisticRegression()
]

for model,label in zip(models,models_name):
    model.fit(X_train,y_train)
    y_pred = model.predict(X_test)
    print(f"Model: {label}")
    print(f"Acurracy: {accuracy_score(y_test,y_pred)}")
    sns.heatmap(confusion_matrix(y_test,y_pred),annot=True)
    plt.title(model)
    plt.show()
     
