# -*- coding: utf-8 -*-
"""Covid.ipynb

Automatically generated by Colaboratory.

"""

# Importing packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setting display
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 127)
pd.set_option('display.max_rows', 100)

# Loading in data
data = pd.read_csv('/content/drive/MyDrive/Datasets/Covid Data.csv')

import re
data = data.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))

"""#EDA and Data Cleaning

##EDA
"""

# General dataset info
data.info()

data.shape

data.head()

data.isnull().sum()

# Setting all feature names to lower case
data.columns = [x.lower() for x in data.columns]

# Examining counts for each feature (all categorical)
for x in data.columns:
  sns.barplot(x=data[x].value_counts().index, y=data[x].value_counts()).set_title(x)
  plt.show()

"""##Pregnant"""

# Seeing what the sex was for people who had '97' as the entry in pregnant
null_pregnant = data[data['pregnant']==97]
null_pregnant['sex'].value_counts()

# All of them were males, changing the '97' entries to '2' for non-pregnant
data.loc[data['pregnant']==97, 'pregnant'] = 2

"""##Age"""

# Creating bins for age groups
bins = [0, 3, 13, 20, 40, 60, 80, 100]
data['age_bins'] = pd.cut(data['age'], bins)

# Checking how many in each age group
data['age_bins'].value_counts()

# Visualizing amount in each age group
sns.barplot(x=data['age_bins'].value_counts().index, y=data['age_bins'].value_counts()).set_title("Age bins")
plt.ylabel('Count')
plt.show()

"""##Covid Positive"""

# Creating feature for if a patient had covid
data['covid_pos']=0

# Setting those who had covid to 1
data.loc[data['clasiffication_final'] <= 3, 'covid_pos'] = 1
# Setting those who did not have covid or an inconclusive test to 0
data.loc[data['clasiffication_final'] >= 4, 'covid_pos'] = 0

# Visualizing hospitilization rate of those with and without covid
table = pd.crosstab(data['covid_pos'], data.patient_type)
table.div(table.sum(1).astype(float), axis=0).plot(kind='bar', stacked=False)

# Labels
legend = ['Sent Home', 'Hospitalized']
plt.legend(labels=legend)
plt.ylabel("Rate")

plt.show()

# Reducing dataset to only patients with Covid, only trying to predict what patients with Covid would be hospitalized
data = data.loc[data['covid_pos']==1]

data.shape

"""##Nulls"""

# Choosing features that had to do with pre-existing conditions
feats = ['sex', 'pneumonia', 'pregnant', 'diabetes', 'copd', 'asthma', 'inmsupr', 'hipertension', 'other_disease', 'cardiovascular',
         'obesity', 'renal_chronic', 'tobacco']

# Removing data where there was missing data (values 97 or greater)
for x in feats:
    data = data[data[x]<97]

# Adding age groups to features
feats.append('age_bins')

"""##Examining Outcomes"""

# Changing number entries to 'F' or 'M' it more clear if patient was female or male
data['sex'].loc[data['sex']==1]='F'
data['sex'].loc[data['sex']==2]='M'

# Changing binaries to 'Y' or 'N' to make it more clear if patient had a condition or not
conditions = ['pneumonia', 'pregnant', 'diabetes', 'copd', 'asthma', 'inmsupr', 'hipertension', 'other_disease', 'cardiovascular', 'obesity',
              'renal_chronic', 'tobacco']
for x in conditions:
  data[x].loc[data[x]==1]='Y'
  data[x].loc[data[x]==2]='N'

# Visualizing hospitalization rate for each condition
for x in feats:
  table = pd.crosstab(data[x], data.patient_type)
  table.div(table.sum(1).astype(float), axis=0).plot(kind='bar', stacked=False)

  # Labels
  plt.legend(labels=legend)
  plt.ylabel("Rate")
  plt.show()

  # Hospitalization rates
  print('Hospitalization rate of left column: ' + str(round(table.iloc[0,1]/(table.iloc[0,1]+table.iloc[0,0]), 4)))
  print('Hospitalization rate of right column: ' + str(round(table.iloc[1,1]/(table.iloc[1,1]+table.iloc[1,0]), 4)))
  print('*'*100)

# Males slightly more likely to be hospitalized, pneumonia patients way more likely to be hospitalized, seeing if condition is more common in males
table = pd.crosstab(data['sex'], data.pneumonia)
table.div(table.sum(1).astype(float), axis=0).plot(kind='bar', stacked=False)
plt.show()

# Pneumonia rates
print('Pneumonia rate in females: ' + str(round(table.iloc[0,1]/(table.iloc[0,1]+table.iloc[0,0]), 4)))
print('Pneumonia rate in males: ' + str(round(table.iloc[1,1]/(table.iloc[1,1]+table.iloc[1,0]), 4)))

"""##Dummies"""

# Making a copy of dataset
processed_data = data.copy()

# Defining function to create dummy variables
def create_dummies(df, column_name):
    # Creating dummies
    dummies = pd.get_dummies(df[column_name], prefix=column_name, drop_first=True)
    # Concatenating dummies to dataframe
    df = pd.concat([df, dummies], axis=1)
    # Dropping original columns
    df = df.drop(columns=column_name)
    return df

# Temporarily adding patient type to features to create dummy variable for it
feats.append('patient_type')

# Iterating through features to create dummies
for x in feats:
  processed_data = create_dummies(processed_data, x)

# Removing patient type from features
feats.remove('patient_type')

# Renaming features to be more clear/consistent
processed_data = processed_data.rename(columns={'patient_type_2':'hospitalized', 'age_bins_(3, 13]':'age_bins_(3, 13)',
                                                'age_bins_(13, 20]':'age_bins_(13, 20)', 'age_bins_(20, 40]':'age_bins_(20, 40)',
                                                'age_bins_(40, 60]':'age_bins_(40, 60)', 'age_bins_(60, 80]':'age_bins_(60, 80)',
                                                'age_bins_(80, 100]':'age_bins_(80, 100)'})

# Initializing feature for baby age group
processed_data['age_bins_(0, 3)']=0

# Creating mask that finds those who aren't in any current age group
mask = (processed_data['age_bins_(3, 13)'] == 0) & (processed_data['age_bins_(80, 100)'] == 0) & (processed_data['age_bins_(13, 20)'] == 0) & (processed_data['age_bins_(20, 40)'] == 0) & (processed_data['age_bins_(40, 60)'] == 0) & (processed_data['age_bins_(60, 80)'] == 0)

# Setting those who aren't currently in an age group to be in the baby age group
processed_data.loc[mask, 'age_bins_(0, 3)'] = 1

# Creating feature set
processed_feats = ['sex_M',	'pneumonia_Y',	'pregnant_Y',	'diabetes_Y',	'copd_Y',	'asthma_Y',	'inmsupr_Y',	'hipertension_Y',
                   'other_disease_Y',	'cardiovascular_Y',	'obesity_Y',	'renal_chronic_Y',	'tobacco_Y',	'age_bins_(0, 3)', 'age_bins_(3, 13)',
                   'age_bins_(13, 20)',	'age_bins_(20, 40)',	'age_bins_(40, 60)',	'age_bins_(60, 80)',	'age_bins_(80, 100)', 'hospitalized']

# Setting dataframe to contain relevant features
processed_data = processed_data[processed_feats]

# Removing target variable from features
processed_feats.remove('hospitalized')

"""#Model Building

##Baseline Model
"""

from sklearn.metrics import log_loss

## Function to calculate baseline log loss based on guessing from the class ratio
## Function obtained from https://medium.com/@fzammito/whats-considered-a-good-log-loss-in-machine-learning-a529d400632d
def calculate_log_loss(class_ratio,multi=10000):

    if sum(class_ratio)!=1.0:
        print("warning: Sum of ratios should be 1 for best results")
        class_ratio[-1]+=1-sum(class_ratio)  # add the residual to last class's ratio

    actuals=[]
    for i,val in enumerate(class_ratio):
        actuals=actuals+[i for x in range(int(val*multi))]


    preds=[]
    for i in range(multi):
        preds+=[class_ratio]

    return (log_loss(actuals, preds))

# Getting ratios
processed_data['hospitalized'].value_counts()

print(277940/(277940+109656))
print(109656/(109656+277940))

# Calculating baseline log loss
calculate_log_loss([0.72,0.28])

"""##Initial Models"""

# Installing models
!pip install catboost
!pip install lightgbm==2.2.3

# Importing packages
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
import lightgbm as lgb

from sklearn.model_selection import cross_val_score

# Initializing models
model_names = ['Logistic Regression', 'Random Forest', 'XGBoost', 'Catboost', 'LightGBM']
models = [LogisticRegression(), RandomForestClassifier(), XGBClassifier(), CatBoostClassifier(verbose=False),
          lgb.LGBMClassifier()]

# Looping through models and seeing initial log loss scores with default parameters
for model, name in zip(models, model_names):
    print(name + ' log loss: ' +
          str(cross_val_score(model, processed_data[processed_feats], processed_data['hospitalized'], cv=5, scoring='neg_log_loss').mean()))

"""##LightGBM"""

# Importing packages
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV

# Initializing LGBM model
lgbm = lgb.LGBMClassifier()

# Creating parameter grid for random grid search
rnd_param_grid = {'num_leaves':[10, 20, 31, 50, 100],
              'min_child_samples':[1, 10, 20, 30, 50],
              'max_depth':[-1, 5, 10, 20],
              'learning_rate':[0.01, 0.05, 0.1, 0.2, 0.3],
              'reg_alpha':[0, 0.01, 0.05, 0.1],
              'n_iter':[50, 75, 100, 200, 500]}

# Creating randomized grid search
rnd_lgbm = RandomizedSearchCV(lgbm, param_distributions = rnd_param_grid, n_iter = 300, cv = 3, verbose = True, n_jobs = -1,
                              scoring='neg_log_loss')
# Fitting randomized grid search
rnd_lgbm.fit(processed_data[processed_feats], processed_data['hospitalized'])

# Printing best parameters from randomized grid search
print(rnd_lgbm.best_params_)

# Creating new parameter grid from randomized grid search parameters
param_grid = {'reg_alpha': [0, 0.01],
              'num_leaves': [100, 150, 200],
              'n_iter': [60, 75, 90],
              'min_child_samples': [1, 5],
              'max_depth': [5, 10, 15],
              'learning_rate': [0.02, 0.05, 0.07]}

# Creating grid search
grid_lgbm = GridSearchCV(lgbm, param_grid=param_grid, cv=3, verbose=2, n_jobs=-1, scoring='neg_log_loss')
# Fitting grid search
grid_lgbm.fit(processed_data[processed_feats], processed_data['hospitalized'])

# Printing best parameters from grid search
print(grid_lgbm.best_params_)

# Creating LGBM model with tuned hyperparameters
lgbm = lgb.LGBMClassifier(learning_rate=0.05, max_depth=15, min_child_samples=5, n_iter=75, num_leaves=100, reg_alpha=0.01)

# Evaluating tuned model
print(cross_val_score(lgbm, processed_data[processed_feats], processed_data['hospitalized'], cv=5, scoring='neg_log_loss').mean())

"""#Predictions"""

from sklearn.model_selection import cross_val_predict

# Generating hospitalization probability predictions
prob = cross_val_predict(lgbm, processed_data[processed_feats], processed_data['hospitalized'], cv=5, method='predict_proba')
prob = pd.Series(prob[:,1], index=processed_data.index)

# Generating hospitalization predictions
pred = cross_val_predict(lgbm, processed_data[processed_feats], processed_data['hospitalized'], cv=5)

# Concatenating to dataset
processed_data['hospitalized_prob'] = prob
processed_data['hospitalized_pred'] = pred

processed_data.head()

"""#Model Evaluation

##Initial Evaluation
"""

pip install ml_insights

# Importing evaluation packages
import ml_insights as mli
from sklearn.metrics import confusion_matrix
from sklearn.calibration import calibration_curve
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import brier_score_loss

# Confusion matrix
confusion_matrix(processed_data['hospitalized'], processed_data['hospitalized_pred'])

# Accuracy, recall, and precision scores
print('Accuracy:', (264754+73557)/(264754+13186+36099+73557))
print('Recall (TPR):', recall_score(processed_data['hospitalized'], processed_data['hospitalized_pred']))
print('Precision:', precision_score(processed_data['hospitalized'], processed_data['hospitalized_pred']))

# AUC ROC Curve
fpr, tpr, _ = roc_curve(processed_data['hospitalized'], processed_data['hospitalized_prob'])
plt.plot(fpr, tpr)
plt.ylabel("True Positve Rate")
plt.xlabel("False Positive Rate")
plt.title("ROC Curve")
plt.show()

# AUC ROC Score
print("AUC ROC Score:", roc_auc_score(processed_data['hospitalized'], processed_data['hospitalized_prob']))

import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms

# Calibration curve

# Generating probability bins
prob_true, prob_pred = calibration_curve(processed_data['hospitalized'], processed_data['hospitalized_prob'], n_bins=10)

fig, ax = plt.subplots()

# Plotting calibration curve
plt.plot(prob_pred, prob_true, marker='o')

# Ideal line
line = mlines.Line2D([0, 1], [0, 1], color='black')
transform = ax.transAxes
line.set_transform(transform)
ax.add_line(line)

# Labels
fig.suptitle('Calibration plot')
ax.set_xlabel('Predicted probability')
ax.set_ylabel('True probability')

# View
plt.xlim([0,1])
plt.ylim([0,1])
plt.xticks(np.arange(0, 1.01, 0.1))
plt.yticks(np.arange(0, 1.01, 0.1))
plt.grid()
plt.show()

# Calibration curve using ML Insights and confidence intervals
plt.figure(figsize=(15,5))
mli.plot_reliability_diagram(processed_data['hospitalized'], processed_data['hospitalized_prob'],show_histogram=True)

# Evaluating probability predictions
print('Brier Score:', brier_score_loss(processed_data['hospitalized'], processed_data['hospitalized_prob']))
print('Log Loss:', log_loss(processed_data['hospitalized'], processed_data['hospitalized_prob']))

"""##Calibrating Model"""

# Importing packages
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV

## Calibrating the model
## As I look back on this code after publishing my article I realize that the validation and test datasets were the exact same,
## meaning I fitted and predicted the calibrated classifier on the same dataset, so these calibrated predictions are overfit

# Splitting in to 80/10/10 train, validation, and test datasets
X_train_raw, X_test, y_train_raw, y_test = train_test_split(processed_data[processed_feats], processed_data['hospitalized'],
                                                            test_size=0.1, shuffle=False)
X_train, X_val, y_train, y_val = train_test_split(processed_data[processed_feats], processed_data['hospitalized'],
                                                            test_size=0.1, shuffle=False)

# Fitting base model on train dataset
lgbm.fit(X_train, y_train)

# Creating calibrated classifier and fitting on validation set
calibrated_lgbm = CalibratedClassifierCV(lgbm, cv='prefit', method='isotonic')
calibrated_lgbm.fit(X_val, y_val)

# Generating calibrated probabilities from test dataset
calibrated_probs = calibrated_lgbm.predict_proba(X_test)[:,1]

# Evaluating calibrated probabilities
print('Brier Score:', brier_score_loss(y_test, calibrated_probs))
print('Log Loss:', log_loss(y_test, calibrated_probs))

# Calibration plot for calibrated probabilities
plt.figure(figsize=(15,5))
mli.plot_reliability_diagram(y_test, calibrated_probs,show_histogram=True)

# Making copy of dataframe
new_df = X_test.copy()

# Adding hospitalized and the predictions
new_df['hospitalized'] = y_test
new_df['hospitalized_prob'] = calibrated_probs
new_df['hospitalized_pred'] = calibrated_lgbm.predict(X_test)

# Confusion matrix
confusion_matrix(new_df['hospitalized'], new_df['hospitalized_pred'])

# Accuracy, recall, and precision scores
print('Accuracy:', (34858+2203)/(34858+509+1190+2203))
print('Recall (TPR):', recall_score(new_df['hospitalized'], new_df['hospitalized_pred']))
print('Precision:', precision_score(new_df['hospitalized'], new_df['hospitalized_pred']))

# ROC AUC curve for calibrated probabilities
_fpr, _tpr, __ = roc_curve(new_df['hospitalized'], new_df['hospitalized_prob'])

plt.plot(_fpr, _tpr)
plt.ylabel("True Positve Rate")
plt.xlabel("False Positive Rate")
plt.title("ROC Curve")
plt.show()

print("ROC AUC Score:", roc_auc_score(new_df['hospitalized'], new_df['hospitalized_prob']))

"""#Analyzing Bad Recall"""

# Feature for seeing people who didn't have any pre exisiting condition
new_df['no_condition']=0
mask = ((new_df['pneumonia_Y'] == 0) & (new_df['pregnant_Y'] == 0) & (new_df['diabetes_Y'] == 0) & (new_df['copd_Y'] == 0) &
 (new_df['asthma_Y'] == 0) & (new_df['inmsupr_Y'] == 0) & (new_df['hipertension_Y'] == 0) & (new_df['other_disease_Y'] == 0) &
  (new_df['cardiovascular_Y'] == 0) & (new_df['obesity_Y'] == 0) & (new_df['renal_chronic_Y'] == 0) & (new_df['tobacco_Y'] == 0))
new_df.loc[mask, 'no_condition']=1

# Creating dataframe for those who were hospitalized but weren't predicted to be
mask = (new_df['hospitalized'] == 1) & (new_df['hospitalized_pred'] == 0)
df_wrong = new_df[mask]

# Creating dataframe for those who were hospitalized in general
hospitalized_df = new_df[new_df['hospitalized']==1]

for x in df_wrong.columns:
  fig, ax = plt.subplots(1,2, figsize = (15,4))
  # Plotting condition frequency for hospitalized patients
  sns.barplot(x=hospitalized_df[x].value_counts().index, y=hospitalized_df[x].value_counts(), ax=ax[0]).set_title('Hospitalized patients: ' + x)
  # Plotting condition frequency for those who were not predicted to be hospitalized but were
  sns.barplot(x=df_wrong[x].value_counts().index, y=df_wrong[x].value_counts(), ax=ax[1]).set_title('Incorrect non-hospitalized prediction: ' + x)
  plt.show()

"""#SHAP"""

pip install shap

import shap

# Creating tree explainer
explainer = shap.TreeExplainer(lgbm)

# Generating SHAP values for train dataset
shap_values_train = explainer.shap_values(X_train)

# Generating SHAP values for test dataset
shap_values_test = explainer.shap_values(X_test)

# SHAP bar plot for train dataset
shap.summary_plot(shap_values_train, X_train)

# SHAP bar plot for test dataset
shap.summary_plot(shap_values_test, X_test)

# SHAP beeswarm plot for train dataset for those that were hospitalized
shap.summary_plot(shap_values_train[1], X_train)

# SHAP beeswarm plot for test dataset for those that were hospitalized
shap.summary_plot(shap_values_test[1], X_test)
