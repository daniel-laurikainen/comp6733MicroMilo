import sklearn
import torch
import matplotlib
import os
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils import Bunch
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


def load_leaf_reflectance_data(csv_path="leaf_reflectance_classification_data.csv"):

    # Load the CSV
    df = pd.read_csv(csv_path)

    # Drop rows with all-zero reflectance (likely FLS readings)
    reflectance_cols = [col for col in df.columns if 'nm' in col]
    df = df[~(df[reflectance_cols].sum(axis=1) == 0)]

    # Extract features (wavelength columns)
    X = df[reflectance_cols].values

    # Encode labels: Healthy, Dry, Over Watered
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Condition"])

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return Bunch(
        data=X_scaled,
        target=y,
        target_names=label_encoder.classes_,
        feature_names=reflectance_cols,
        DESCR="Leaf reflectance classification dataset (Healthy, Dry, Over Watered)"
    )

def load_leaf_data2(csv_path="leaf_reflectance_classification_data.csv"):

    # Load the CSV
    df = pd.read_csv(csv_path)

    # Drop rows with all-zero reflectance (likely FLS readings)
    reflectance_cols = [col for col in df.columns if 'nm' in col]
    df = df[~(df[reflectance_cols].sum(axis=1) == 0)]

    # Recode Condition to binary: Healthy vs Unhealthy
    df["Condition"] = df["Condition"].apply(lambda x: "Healthy" if x == "Healthy" else "Unhealthy")

    # Extract features
    X = df[reflectance_cols].values

    # Encode binary labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Condition"])  # Healthy=0, Unhealthy=1

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return Bunch(
        data=X_scaled,
        target=y,
        target_names=label_encoder.classes_,
        feature_names=reflectance_cols,
        DESCR="Leaf reflectance binary classification dataset (Healthy vs Unhealthy)"
    )

def load_data(folder_path="./data/scans"):
    # Find all CSV files in the directory
    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".csv")
    ]

    # Load and combine all files
    df_list = [pd.read_csv(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)

    # Keep only reflectance feature columns
    reflectance_cols = [col for col in df.columns if col.startswith("channel_")]
    df = df.dropna(subset=reflectance_cols)

    # Drop rows where all reflectance values are zero
    df = df[~(df[reflectance_cols].sum(axis=1) == 0)]

    # Extract labels from the 'description' field
    df["Condition"] = df["description"].str.lower().apply(
        lambda desc: "Healthy" if "health" in desc else "Unhealthy"
    )

    # Features and labels
    X = df[reflectance_cols].values
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Condition"])

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return Bunch(
        data=X_scaled,
        target=y,
        target_names=label_encoder.classes_,
        feature_names=reflectance_cols,
        DESCR="Binary leaf reflectance classification dataset (Healthy vs Unhealthy)"
    )


def print_classification_metrics(clf, X_train, y_train, X_test, y_test):
    y_train_pred = clf.predict(X_train)
    y_test_pred = clf.predict(X_test)

    print("- Training Accuracy: {:.2f}".format(accuracy_score(y_train, y_train_pred)))
    print("- Testing Accuracy: {:.2f}".format(accuracy_score(y_test, y_test_pred)))
    print("- Confusion Matrix (Test):\n", confusion_matrix(y_test, y_test_pred))
    print("- Classification Report (Test):\n", classification_report(y_test, y_test_pred))


def tune_svc_classifier(X, y):
    print("Tuning SVC...")
    params = {
        'kernel': ['linear', 'rbf'],
        'C': [0.1, 1, 10],
        'gamma': ['scale', 'auto']
    }
    clf = GridSearchCV(SVC(), params, cv=5, scoring='accuracy')
    clf.fit(X, y)
    print("Best SVC parameters:", clf.best_params_)
    return clf

def tune_knn_classifier(X, y):
    print("Tuning KNN...")
    params = {
        'n_neighbors': [1, 3, 5, 7],
        'weights': ['uniform', 'distance']
    }
    clf = GridSearchCV(KNeighborsClassifier(), params, cv=5, scoring='accuracy')
    clf.fit(X, y)
    print("Best KNN parameters:", clf.best_params_)
    return clf

def tune_rf_classifier(X, y):
    print("Tuning Random Forest...")
    params = {
        'n_estimators': [10, 50, 100],
        'max_depth': [None, 5, 10]
    }
    clf = GridSearchCV(RandomForestClassifier(), params, cv=5, scoring='accuracy')
    clf.fit(X, y)
    print("Best RF parameters:", clf.best_params_)
    return clf


# data = load_leaf_reflectance_data()
data = load_leaf_data2()

X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

clf_svc = tune_svc_classifier(X_train, y_train)
clf_knn = tune_knn_classifier(X_train, y_train)
clf_rf = tune_rf_classifier(X_train, y_train)

print("\n--- SVC ---")
print_classification_metrics(clf_svc, X_train, y_train, X_test, y_test)

print("\n--- KNN ---")
print_classification_metrics(clf_knn, X_train, y_train, X_test, y_test)

print("\n--- Random Forest ---")
print_classification_metrics(clf_rf, X_train, y_train, X_test, y_test)
