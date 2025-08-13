#Total failure , spent hours and nothing works

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import LabelEncoder
import factor_analyzer as fa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,confusion_matrix
from xgboost import XGBClassifier
from imblearn.combine import SMOTETomek

categorical_values = ['Diabetes','Family History',
                      'Smoking','Obesity','Alcohol Consumption',
                      'Diet','Previous Heart Problems','Gender']

label = ['Heart Attack Risk']

df = pd.read_csv('./dataIN/heart_attack_risk.csv').drop(columns='HAR_Text').dropna()
encoder = LabelEncoder()
df['Gender'] = encoder.fit_transform(df['Gender'])

print(df.describe())
print(df.head())
print(df.info())

#Correlation
print(df.corr())
fg,ax = plt.subplots(figsize=(20,20))
sns.heatmap(df.corr(),vmax=1,vmin=-1,annot=True,fmt='.2f',ax=ax)
plt.show()

df_efa = pd.DataFrame(df.drop(columns=label+categorical_values))
df_efa = (df_efa - df_efa.mean())/df_efa.std()

#Factoriability Test

chi_val,p_val = fa.calculate_bartlett_sphericity(df)
print("Chi-Value: {0}".format(chi_val))
print("Prob-Value: {0}".format(p_val))

model_fa = fa.FactorAnalyzer(n_factors=df_efa.shape[1],rotation=None)
model_fa.fit(df_efa)
eigenvalue,eigenvector = model_fa.get_eigenvalues()
variance = eigenvalue/np.sum(eigenvalue)

print("Varianta Factori: ")
print(variance)

#Criteriul Kaiser
indK = 0
while indK < len(eigenvalue) and eigenvalue[indK]>=1:
    indK+=1

#Criteriul Variantei
indV = 0
var = 0
while indV < len(eigenvalue) and var<0.8:
    var+=variance[indV]
    indV+=1

#Criteriul lui Catell
indC = 0
val = 0.1
diff = []
for i in range(len(eigenvalue)-1):
    diff.append(eigenvalue[i] - eigenvalue[i+1])
while indC < len(diff)-1 and val>=0:
    val = diff[indC]-diff[indC+1]
    indC += 1
    
print("Catell: "+str(indC))
print("Kaiser: "+str(indK))
print("Variatie: "+str(indV))

plt.scatter([i for i in range(len(variance))],variance)
plt.plot([i for i in range(len(variance))],variance)

plt.bar(["F"+str(i+1) for i in range(len(variance))],[0 for x in range(len(variance))])

if indC>0:
    plt.plot([indC-1,indC-1],[0,0.5],color="red")
    plt.annotate("Catell",(indC-1,0.5))

if indK>0:
    plt.plot([indK-1,indK-1],[0,0.5],color="green")
    plt.annotate("Kaiser", (indK-1, 0.5))

if indV>0:
    plt.plot([indV-1,indV-1],[0,0.5],color="yellow")
    plt.annotate("Varianta", (indV-1, 0.5))

plt.show()

fg,ax = plt.subplots(figsize=(20,20))
corr_df = pd.DataFrame(model_fa.loadings_,columns=['F'+str(i+1) for i in range(df_efa.shape[1])],index=df_efa.columns)
sns.heatmap(corr_df,vmax=1,vmin=-1,annot=True,fmt='.2f',ax=ax)
plt.show()

model_fa = fa.FactorAnalyzer(14,rotation='promax')
model_fa.fit(df_efa)
print(model_fa.get_communalities())
df_projected = pd.DataFrame(model_fa.transform(df_efa))
df_projected = df_projected.join(df[label[0]])
print(df_projected)


fg,ax = plt.subplots(figsize=(20,20))
sns.heatmap(df_projected.corr(),vmax=1,vmin=-1,annot=True,fmt='.2f',ax=ax)
plt.show()

#Class Variable distribution
print("Class distribution")
print("1: {0}".format(df[df[label[0]]==1].shape[0]))
print("0: {0}".format(df[df[label[0]]==0].shape[0]))

#Feature distribution


for it in categorical_values:
    sns.countplot(x=df[it])
    plt.title(it)
    plt.show()

#Balancing Features
# sns.countplot(x=df['Gender']*df['Smoking']*df['Diabetes'])
# plt.title("Balanced")

# df['Balanced'] = df['Gender']*df['Smoking']*df['Diabetes']
# df = df.drop(columns=['Gender','Smoking','Diabetes'])

# categorical_values = ['Family History','Balanced','Obesity','Alcohol Consumption',
#                       'Diet','Previous Heart Problems']


#Outlier
# for it in df.drop(columns=categorical_values+label).columns:
#     sns.boxplot(df[it])
#     plt.title(it)
#     plt.show()
        

X_train,X_test,y_train,y_test = train_test_split(df.drop(columns=label),df[label[0]],train_size=0.75)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

smt = SMOTETomek(random_state=42)
X_train,y_train = smt.fit_resample(X_train,y_train)

#Model Selection
model_forest = RandomForestClassifier(n_estimators=150)
model_forest.fit(X_train,y_train)

model_regression = LogisticRegression()
model_regression.fit(X_train,y_train)

model_xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42 )

model_xgb.fit(X_train, y_train)

models = [model_forest,model_regression,model_xgb]
model_types= ["Random Forest","Logistic Regression","Gradient Boost"]

for model,name in zip(models,model_types):
    y_pred = model.predict(X_test)
    
    print("Test Accuracy:{0}".format(accuracy_score(y_test,y_pred)))
    print("Model Precision:{0}".format(precision_score(y_test,y_pred)))
    print("Model Recall:{0}".format(recall_score(y_test,y_pred)))
    sns.heatmap(confusion_matrix(y_test,y_pred),fmt='0.2f',annot=True)
    plt.title(name)
    plt.show()
    
#Thresholds


for model,name in zip(models,model_types):
    y_pred= model.predict_proba(X_test)[:, 1]
    plt.scatter([i for i in range(len(y_pred))],y_pred,c=y_test)
    plt.show()
    