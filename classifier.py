"""
File: classifier.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

Form D Classification using Decision Trees

Library of functions for classification of 
Form D data using a decision tree algorithm.
Functions include data cleaning, model training,
and training set production.
"""
import os
from sklearn import tree, neighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.externals import joblib
from sklearn.cross_validation import cross_val_score
import pandas as pd
import graphviz
import numpy as np
import pprint as pp


def main():
    np.random.seed(1)
    # first, get the good firms and set class to 1
    train = pd.read_csv("data/training/training_firms.csv", header=0, dtype={"ind_group_type": "category"})
    train["class"] = 1

    # then get the bad firms and set the class to 0
    bad = pd.read_csv("data/training/bad_firms.csv", header=0)
    bad["class"] = 0
    bad = bad.sample(frac=1)
    bad = bad.iloc[:647,]

    train = train.append(bad, ignore_index=True)
    print(len(train))
    # modify the data for use with the decision tree algorithm
    train = clean_data(train)
    
    train = train.sample(frac=1)
    # separate the data and train the classification model
    #x = train.ix[:,["state", "min_inv", "tot_off", "tot_sold", "tot_rem", "ind_group_type", "has_non_accred", "num_non_accred", "tot_num_inv", "tot_off_inf", "tot_rem_inf"]]
    x = train.ix[:,["min_inv", "tot_off", "tot_sold", "tot_rem", "ind_group_type", "has_non_accred", "num_non_accred", "tot_num_inv", "tot_off_inf", "tot_rem_inf"]]
    y = train["class"]

    #print(y)

    # when normalizing bad vs. good # of samples
    percent_train = 1
    split = int(1294 * percent_train)
    # when using all data
    #split = 2314 # 80% split of the data
    x_train = x.iloc[:split,]
    y_train = y.iloc[:split,]

    x_test = x.iloc[split:,]
    y_test = y.iloc[split:,]

    os.chdir('/Users/mbyrnes/docs/school/class/ current/cs490/form_d/data/trees/')
    
    classifiers = [
        tree.DecisionTreeClassifier(),
        tree.DecisionTreeClassifier(min_samples_leaf=5),
        tree.DecisionTreeClassifier(min_samples_leaf=10),
        tree.DecisionTreeClassifier(min_samples_leaf=20),
        tree.DecisionTreeClassifier(min_samples_leaf=30),

        tree.DecisionTreeClassifier(max_depth=1),
        tree.DecisionTreeClassifier(max_depth=3),
        tree.DecisionTreeClassifier(max_depth=5),
        tree.DecisionTreeClassifier(max_depth=7),

        tree.DecisionTreeClassifier(max_depth=3, min_samples_leaf=10),
        tree.DecisionTreeClassifier(max_depth=3, min_samples_leaf=20),
        tree.DecisionTreeClassifier(max_depth=3, min_samples_leaf=20),
    ]

    classifiers = [tree.DecisionTreeClassifier(min_samples_leaf=j, max_depth=k) for j in range(5,30,5) for k in range(1,9)]
    params = [(j,k) for j in range(5,30,5) for k in range(1,9)]
    pp.pprint(classifiers)

    for i, clf in enumerate(classifiers):
        tree_clf = train_model(x_train, y_train, clf, i)
        #print(tree_clf.feature_importances_)
        #preds = tree_clf.predict(x_test)
        #match = (preds == y_test)
        #accuracy = float(match.sum()) / len(y_test)
        accuracy = 0
        scores = cross_val_score(estimator=clf, X=x, y=y, cv=10)
        
        print("Model: {1:2} -- Accuracy: {2:.3f}, min_samples_per_leaf: {3}, max_depth: {4}".format(accuracy, i, scores.mean(), params[i][0], params[i][1]))


def train_model(x_train, y_train, tree_clf, i):
    """
    Build a decision tree classification model
    using training data for SEC Form D data.

    Exports an image of the tree and pickles the model
    for later classification.

    Args:
        x_train: training features
        y_train: response vector
    Returns:
        tree_clf: decision tree model
    """
    tree_clf.fit(x_train,y_train)
    
    tree_data = tree.export_graphviz(tree_clf, out_file=None, feature_names=x_train.columns, class_names=["Bad", "Good"], filled=True, rounded=True)
    graph = graphviz.Source(tree_data)
    graph.render("tree_{0}".format(i))
    
    # save the model
    #joblib.dump(tree_clf, "dec_tree_model.pkl")

    return tree_clf


def clean_data(train, categorical = True):
    """
    Cleans and formats the dataset to comply with Scikit's
    decision tree classifier requirements for 
    data types. 

    Args:
        train: training dataset as Pandas data frame
        categorical: bool to identify if categoricals should be encoded
    Returns:
        train: cleaned version of initially supplied argument
    """
    train = train.replace([np.inf], np.nan)

    if categorical:
      enc = LabelEncoder()
      enc.fit(train["ind_group_type"])
      np.save('enc_classes.npy', enc.classes_)
      train["ind_group_type"] = enc.transform(train["ind_group_type"])
      enc2 = LabelEncoder()
      enc2.fit(train["state"])
      np.save('state_classes.npy', enc2.classes_)
      train["state"] = enc2.transform(train["state"])

    train["tot_off_inf"] = (train["tot_off"].isnull())
    train["tot_rem_inf"] = (train["tot_rem"].isnull())
    
    train = train.fillna(0)
    return train

 
def tree_predict(firm):
    """
    Uses already built model to predict a firm's class 
    for use with the web app interface.

    Args:
        firm: one row of data frame
    Returns:
        output: classification by decision tree
    """
    tree_clf = joblib.load('/Users/mbyrnes/docs/school/class/ current/cs490/form_d/dec_tree_model.pkl')
    encoder = LabelEncoder()
    encoder.classes_ = np.load('/Users/mbyrnes/docs/school/class/ current/cs490/form_d/enc_classes.npy')
    state_encoder = LabelEncoder()
    state_encoder.classes_ = np.load('/Users/mbyrnes/docs/school/class/ current/cs490/form_d/state_classes.npy')
    #print(firm[0])
    try:
        firm[0] = state_encoder.transform(firm[0])[0]
    except ValueError:
        firm[0] = 0
    try:
        firm[5] = encoder.transform(firm[5])[0]
    except ValueError:
        firm[5] = 0
    #firm = firm.reshape(11,1)
    response = tree_clf.predict(firm)
    if response == 0:
        output = "Unlikely Fit"
    else:
        output = "Plausible Fit"
    return output


def get_training_data(plausible=True):
    """
    Builds training data from all historical forms
    based on manually selected list of firms that 
    could plausibly be managers for the investments office.
    Also builds a list of firms that would not be a good fit.

    Args:
        plausible: build the plausible or implausible list of firms
    Returns:
        nothing, but writes the training data to a CSV
    """
    df = pd.read_csv("data/all_data.csv", header=1)
    train = pd.DataFrame(columns=df.columns)

    if plausible:
        train_info = [("amansa feeder", None),
                      ("farallon", "ONE MARITIME PLAZA, SUITE 2100"),
                      ("lone balsam", None),
                      ("brookside", None),
                      ("centerbridge", None),
                      ("convexity capital", None),
                      ("fir tree international", None),
                      ("fir tree capital", None),
                      ("gmo tactical", None),
                      ("gmo quality", None),
                      ("hmi capital", None),
                      ("lone star", None),
                      ("premium point", None),
                      ("sankaty", None),
                      ("west face", None),
                      ("wtc multi", None),
                      ("wtc fundamental", None),
                      ("apis global", None),
                      ("apis deep", None), 
                      ("fpcm", None),
                      ("elliott international", None),
                      ("elliott associates", None),
                      ("forester offshore", None),
                      ("cardinal partners", None),
                      ("delphi capital", None)]
    else:
        train_info = [("blackrock", None),
                      ("morgan stanley", None),
                      ("goldman sachs", None),
                      ("bridgewater", None),
                      ("two sigma", None),
                      ("aqr global", None),
                      ("d. e. shaw", None)]

    for name, address in train_info:
        if address != None:
            res = df[(df["name"].str.lower().str.contains(name)) 
                & (df["street2"] == address)]
        else:
            res = df[(df["name"].str.lower().str.contains(name))]
        train = train.append(res)

    if plausible:
        train.to_csv("training_firms.csv")
    else:
        train.to_csv("bad_firms.csv")

    return 0


if __name__ == '__main__':
    main()