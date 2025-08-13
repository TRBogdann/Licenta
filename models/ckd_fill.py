import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier,KNeighborsRegressor
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer,KNNImputer
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.linear_model import LinearRegression
df = pd.read_csv('./dataIN/kidney_disease.csv',index_col=0)


quality = ['rbc','pc','pcc','ba','pcv','wc','rc','htn'
           ,'dm','cad','appet','pe','ane','classification']

df = df.dropna(subset=['htn','dm','cad','appet','pe','ane'])
print(df.info())

for it in quality:
    encoder = LabelEncoder()
    df[it] = encoder.fit_transform(df[it])
    
sns.heatmap(df.corr(),vmin=-1,vmax=1,annot=True)
plt.show()

#1.MICE
#2.BFILL+MICE
#3.FFILL+MICE
#4.KNN+MICE
#5.KNN+KNN

df = df.fillna(np.nan)
print(df.info())
# 1.
imputer = IterativeImputer(estimator=RandomForestRegressor())
df_mice = pd.DataFrame(imputer.fit_transform(df.to_numpy()),columns=df.columns,index=df.index)
print(df_mice.info())
df_mice.to_csv('./dataIN/ckd_fill/mice.csv')

#5
imputer = KNNImputer()
df_knn = pd.DataFrame(imputer.fit_transform(df.to_numpy()),columns=df.columns,index=df.index)
print(df_knn.info())
df_knn.to_csv('./dataIN/ckd_fill/knn.csv')