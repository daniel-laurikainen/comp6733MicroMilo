import sklearn
# import torch
import matplotlib
import os, glob
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils import Bunch
import numpy as np
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.neighbors import KNeighborsRegressor
# from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

# data loader for MVP
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

#data loader for Progress Report
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

#data loader for Final Report
def load_data(folder_path="../data/scans/basil_scans"):
    # Find all CSV files in the directory

    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".csv")
    ]

    # if folder_path is None:
    #     folder_path = [
    #         "../data/scans/leaf_scans",
    #         "../data/scans/basil_scans",
    #         # add more if you want:
    #         # "../data/scans/old_scans",
    #     ]

    # collect all CSVs from all folders (non-recursive)
    # all_files = []
    # for fp in folder_path:
    #     all_files.extend(glob.glob(os.path.join(fp, "*.csv")))
    
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in: {folder_path}")

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

#comprehensive metrics: testing accuracy, precision, recall
def print_classification_metrics(clf, X_train, y_train, X_test, y_test):
    y_train_pred = clf.predict(X_train)
    y_test_pred = clf.predict(X_test)

    print("- Training Accuracy: {:.2f}".format(accuracy_score(y_train, y_train_pred)))
    print("- Testing Accuracy: {:.2f}".format(accuracy_score(y_test, y_test_pred)))
    print("- Confusion Matrix (Test):\n", confusion_matrix(y_test, y_test_pred))
    print("- Classification Report (Test):\n", classification_report(y_test, y_test_pred))

#model tuning to find best parameter
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

#K-fold cross validation 
def evaluate_with_kfold(model, X, y, k=5):
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
    print(f"K-Fold Accuracies ({k} folds):", np.round(scores, 3))
    print("Mean Accuracy: {:.2f}".format(scores.mean()))
    print("Std Deviation: {:.2f}".format(scores.std()))

def evaluate_model_cv_and_test(model, X_train, y_train, X_test, y_test, k=5, name="Model"):
    """
    Prints k-fold CV accuracy (on X_train/y_train) and test-set metrics for the same model.
    Works with either a fitted estimator or a fitted GridSearchCV object.
    Returns a dict of key metrics.
    """
    # Use the tuned estimator if GridSearchCV was used; otherwise use the model itself
    est = model.best_estimator_ if hasattr(model, "best_estimator_") else model

    # ----- Cross-validated accuracy on TRAIN split -----
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    cv_scores = cross_val_score(est, X_train, y_train, cv=skf, scoring='accuracy')
    cv_mean, cv_std = cv_scores.mean(), cv_scores.std()

    # ----- Test metrics on HOLD-OUT set -----
    # (GridSearchCV.best_estimator_ is refit by default; if you passed a plain estimator, ensure it's fit)
    # We'll be safe and fit on X_train if needed.
    try:
        _ = est.predict(X_train[:1])
    except Exception:
        est.fit(X_train, y_train)

    y_train_pred = est.predict(X_train)
    y_test_pred  = est.predict(X_test)

    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc  = accuracy_score(y_test, y_test_pred)
    cm        = confusion_matrix(y_test, y_test_pred)
    report    = classification_report(y_test, y_test_pred)

    # ----- Pretty print -----
    print(f"\n=== {name} ===")
    if hasattr(model, "best_params_"):
        print("Best params:", model.best_params_)
    print(f"K-Fold ({k}) CV Accuracies:", np.round(cv_scores, 3))
    print(f"K-Fold Mean Accuracy: {cv_mean:.3f}  (± {cv_std:.3f})")
    print(f"Train Accuracy: {train_acc:.3f}")
    print(f"Test  Accuracy: {test_acc:.3f}")
    print("Confusion Matrix (Test):\n", cm)
    print("Classification Report (Test):\n", report)

    return {
        "name": name,
        "best_params": getattr(model, "best_params_", None),
        "cv_scores": cv_scores,
        "cv_mean": cv_mean,
        "cv_std": cv_std,
        "train_acc": train_acc,
        "test_acc": test_acc,
        "confusion_matrix": cm,
        "classification_report": report,
    }

data = load_data()

X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

clf_svc = tune_svc_classifier(X_train, y_train)
clf_knn = tune_knn_classifier(X_train, y_train)
clf_rf = tune_rf_classifier(X_train, y_train)

# print("\n--- SVC ---")
# print_classification_metrics(clf_svc, X_train, y_train, X_test, y_test)
# evaluate_with_kfold(clf_svc, X_train, y_train)

# print("\n--- KNN ---")
# print_classification_metrics(clf_knn, X_train, y_train, X_test, y_test)
# evaluate_with_kfold(clf_knn, X_train, y_train)

# print("\n--- Random Forest ---")
# print_classification_metrics(clf_rf, X_train, y_train, X_test, y_test)
# evaluate_with_kfold(clf_rf, X_train, y_train)


svc_metrics = evaluate_model_cv_and_test(clf_svc, X_train, y_train, X_test, y_test, k=5, name="SVC")
knn_metrics = evaluate_model_cv_and_test(clf_knn, X_train, y_train, X_test, y_test, k=5, name="KNN")
rf_metrics  = evaluate_model_cv_and_test(clf_rf,  X_train, y_train, X_test, y_test, k=5, name="Random Forest")

# Save the pre-trained KNN model 
import pickle

# with open("RF_basil_model.pkl", "wb") as f:
#     pickle.dump(clf_rf.best_estimator_, f)

### Usage of the saved model: ###

# with open("knn_leaf_model.pkl", "rb") as f:
#     knn_model = pickle.load(f)

# pred = knn_model.predict(X_new_scaled)
