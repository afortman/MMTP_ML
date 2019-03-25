import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import lightgbm as lgb

# https://www.kaggle.com/ezietsman/simple-python-lightgbm-example
# https://medium.com/@pushkarmandot/https-medium-com-pushkarmandot-what-is-lightgbm-how-to-implement-it-how-to-fine-tune-the-parameters-60347819b7fc

### import dataset
dataset = pd.read_csv('train.csv')

### values we care about when training
x = dataset.iloc[:, 7:15].values

### signal vs bkg
y = dataset.iloc[:, 0].values

#print(x[0])
#print(len(y))

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.25)


###### converting into an lgb dataset
d_train = lgb.Dataset(x_train, label=y_train)

###### learn more about and ajust these!!!
params = {}
params['learning_rate'] = 0.1
params['boosting_type'] = 'gbdt'
params['objective'] = 'binary'
params['metric'] = 'binary_logloss'
params['sub_feature'] = 0.5
params['num_leaves'] = 30
params['min_data'] = 50
params['max_depth'] = 10


# actually using lightgbm
model = lgb.train(params, d_train, 100)


#Prediction using test values
y_pred = model.predict(x_test)

#print(len(y_pred))

#convert into binary values
for i in range(0,len(y_pred)):
    if y_pred[i]>=.5:       # setting threshold to .5
        y_pred[i]=1
    else:
        y_pred[i]=0

#print(y_pred) #### now binary


#Confusion matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)
#Accuracy
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_pred,y_test)
print(accuracy)
