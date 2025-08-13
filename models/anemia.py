import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix,accuracy_score
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv('./dataIN/anemia.csv')
print(df.info())
print(df.describe())

sns.heatmap(df.corr(),vmin=-1,vmax=1,annot=True,cmap='coolwarm')
plt.show()

label = df['Result']
df_std = df.drop(columns=['Result','Gender'])
df_std = (df_std - df_std.mean())/df_std.std()

for i in range(len(df_std.columns)):
    for j in range(i+1,len(df_std.columns)-1):
        plt.xlabel(df_std.columns[i])
        plt.ylabel(df_std.columns[j])
        plt.scatter(df_std[df_std.columns[i]],df_std[df_std.columns[j]],c=label)
        plt.show()


X_train,X_test,y_train,y_test = train_test_split(df_std,label,train_size=0.75,random_state=42)      
lda = LinearDiscriminantAnalysis(n_components=1)
X_train_lda = pd.DataFrame(lda.fit_transform(X_train,y_train),index=X_train.index,columns=['Discriminant'])
X_test_lda = pd.DataFrame(lda.transform(X_test),index=X_test.index,columns=['Discriminant'])

y_pred = lda.predict(X_test)

print('LDA Score:')
print(f'Accuracy: {accuracy_score(y_test,y_pred)}')
sns.heatmap(confusion_matrix(y_test,y_pred),annot=True,fmt='.0f')
plt.show()

X_train_lda = X_train_lda.join(df['Gender'])
X_test_lda = X_test_lda.join(df['Gender'])

tree1 = DecisionTreeClassifier(random_state=42,max_depth=10)
tree2 = DecisionTreeClassifier(random_state=42,max_depth=10)

tree1.fit(X_train,y_train)
tree2.fit(X_train_lda,y_train)

svm = SVC(random_state=42)
svm.fit(X_train,y_train)

models = [svm,tree1,tree2]
names = ['SVM','Tree_Classifier','Tree_LDA']
tests = [X_test,X_test,X_test_lda]

for model,name,test in zip(models,names,tests):
    y_pred = model.predict(test)
    print(f'{name} Score:')
    print(f'Accuracy: {accuracy_score(y_test,y_pred)}')
    sns.heatmap(confusion_matrix(y_test,y_pred),annot=True,fmt='.0f')
    plt.title(name)
    plt.show()
