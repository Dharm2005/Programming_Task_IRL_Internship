import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score

# Load data
df = pd.read_csv("../data/clean_reviews.csv")

X = df['clean_text']
y = df['Sentiment']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

mlflow.set_experiment("Flipkart_Sentiment_Analysis")

# We will try different hyperparameters
max_feature_values = [1000, 3000, 5000, 7000]

for mf in max_feature_values:

    with mlflow.start_run(run_name=f"LR_TFIDF_{mf}"):

        # Log parameters
        mlflow.log_param("vectorizer", "TF-IDF")
        mlflow.log_param("max_features", mf)
        mlflow.log_param("model", "LogisticRegression")

        # Vectorization
        tfidf = TfidfVectorizer(max_features=mf)

        X_train_vec = tfidf.fit_transform(X_train)
        X_test_vec = tfidf.transform(X_test)

        # Train model
        model = LogisticRegression()
        model.fit(X_train_vec, y_train)

        # Predictions
        preds = model.predict(X_test_vec)

        # Metrics
        f1 = f1_score(y_test, preds)
        precision = precision_score(y_test, preds)
        recall = recall_score(y_test, preds)

        print(f"Run with max_features={mf} → F1 Score: {f1}")

        # Log metrics
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)

        # Log artifacts
        mlflow.sklearn.log_model(model, "sentiment_model")
        mlflow.sklearn.log_model(tfidf, "tfidf_vectorizer")

print("All MLflow runs completed!")
