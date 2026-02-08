from prefect import task, flow

import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score


@task
def load_data():
    df = pd.read_csv("../data/clean_reviews.csv")
    return df


@task
def split_data(df):
    X = df['clean_text']
    y = df['Sentiment']

    return train_test_split(X, y, test_size=0.2, random_state=42)


@task
def train_and_log(X_train, X_test, y_train, y_test):

    mlflow.set_experiment("Flipkart_Sentiment_Analysis_Prefect")

    with mlflow.start_run(run_name="Prefect_Automated_Run"):

        max_features = 5000

        mlflow.log_param("vectorizer", "TF-IDF")
        mlflow.log_param("max_features", max_features)
        mlflow.log_param("model", "LogisticRegression")

        tfidf = TfidfVectorizer(max_features=max_features)

        X_train_vec = tfidf.fit_transform(X_train)
        X_test_vec = tfidf.transform(X_test)

        model = LogisticRegression()
        model.fit(X_train_vec, y_train)

        preds = model.predict(X_test_vec)

        f1 = f1_score(y_test, preds)

        mlflow.log_metric("f1_score", f1)

        mlflow.sklearn.log_model(model, "sentiment_model")

    return f1


@flow(name="Sentiment_Training_Workflow")
def sentiment_pipeline():

    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)
    score = train_and_log(X_train, X_test, y_train, y_test)

    print("F1 Score from Prefect Pipeline:", score)


if __name__ == "__main__":
    # This replaces the old Deployment API
    sentiment_pipeline.serve(
        name="daily_training",
        cron="0 0 * * *"   # runs once every day
    )
