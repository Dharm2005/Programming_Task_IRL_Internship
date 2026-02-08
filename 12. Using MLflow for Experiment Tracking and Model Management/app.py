import streamlit as st
import pickle
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Load saved model and vectorizer
model = pickle.load(open("../models/sentiment_model.pkl", "rb"))
tfidf = pickle.load(open("../models/tfidf_vectorizer.pkl", "rb"))

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

st.title("Flipkart Review Sentiment Analyzer")

user_input = st.text_area("Enter Review Text")

if st.button("Predict Sentiment"):

    cleaned = clean_text(user_input)
    vector = tfidf.transform([cleaned])
    prediction = model.predict(vector)

    if prediction[0] == 1:
        st.success("Positive Review 😊")
    else:
        st.error("Negative Review 😞")
