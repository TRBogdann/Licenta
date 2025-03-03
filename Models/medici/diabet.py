import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import outlier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score,confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

df = pd.read_csv('dataIN/diabetes_dataset.csv')
df = df.dropna()

#Corelations
sns.heatmap(df.corr(),vmin=-1,vmax=1,cmap='coolwarm',annot=True)
plt.show()


#Balance
categorical_features = ['FamilyHistory', 'Hypertension','DietType']
for it in categorical_features:
    sns.countplot(x=df[it])
    plt.title(it)
    plt.show()


#Feature Selection
df = df.drop(columns=['HbA1c','WaistCircumference','HipCircumference','MedicationUse','DietType','Hypertension'])


#Outliers
rows_prev = df.shape[0]
remove_list = []

for it in df.columns:
    if it != 'Outcome':
        sns.boxplot(df[it])
        plt.title(it)
        plt.show()
    
print("Outlier percentage:")
for it in df.columns:
    if it != 'Outcome':    
        lower_bound,upper_bound = outlier.outlier_interval(df,it)
        outliers = df[(df[it]<lower_bound)|(df[it]>upper_bound)]
        percentage = len(outliers)/df.shape[0]
        if percentage<=0.01:
            remove_list.append(it)

for it in remove_list:
    df = outlier.remove_outliers(df,it)
    
print("Removed {0} instances from the ".format(rows_prev-df.shape[0]))
print("Reamining size:{0}%".format(((df.shape[0])/rows_prev)*100))

#Standardization
X_train,X_test,Y_train,Y_test = train_test_split(df,df['Outcome'],train_size=0.75,random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

#Model Selection
model_forest = RandomForestClassifier(n_estimators=150)
model_forest.fit(X_train,Y_train)

model_svm = SVC()
model_svm.fit(X_train,Y_train)

model_regression = LogisticRegression()
model_regression.fit(X_train,Y_train)

models = [model_forest,model_regression,model_svm]
model_types= ["Random Forest","Logistic Regression","SVM"]

for model,name in zip(models,model_types):
    Y_pred = model.predict(X_test)
    print("Test Accuracy:{0}".format(accuracy_score(Y_test,Y_pred)))
    print("Model Precision:{0}".format(precision_score(Y_test,Y_pred)))
    print("Model Recall:{0}".format(recall_score(Y_test,Y_pred)))
    sns.heatmap(confusion_matrix(Y_test,Y_pred),annot=True)
    plt.title(name)
    plt.show()