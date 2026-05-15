import time
import os
import joblib
from typing import Tuple, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

# A realistic sample dataset for training the intent classifier
TRAINING_DATA = [
    # reminders
    ("Remind me to buy milk tomorrow at 5 PM", "reminder"),
    ("Set an alarm for 7 AM", "reminder"),
    ("Don't forget to call mom this weekend", "reminder"),
    ("Add eggs to the grocery list", "reminder"),
    ("Ping me in 10 minutes", "reminder"),
    ("Remind me about the meeting at 3", "reminder"),
    ("Set a timer for 15 minutes", "reminder"),
    ("I need to remember to pay the bills", "reminder"),
    ("Alert me when it's time to go", "reminder"),
    ("Remind me to call John later", "reminder"),
    ("Make sure I don't forget my keys", "reminder"),
    
    # emotional-support
    ("I'm feeling really sad today and I don't know why", "emotional-support"),
    ("Can you just listen to me? I had a terrible day.", "emotional-support"),
    ("I'm feeling so overwhelmed and stressed out.", "emotional-support"),
    ("Everything is going wrong, I just need someone to talk to.", "emotional-support"),
    ("I feel lonely.", "emotional-support"),
    ("I'm so exhausted and burnt out", "emotional-support"),
    ("I need some advice, I'm feeling lost", "emotional-support"),
    ("I'm having a really hard time right now", "emotional-support"),
    ("I feel like giving up", "emotional-support"),
    ("Nobody understands what I'm going through", "emotional-support"),
    ("I'm just so anxious about the future", "emotional-support"),

    # action-item
    ("I need to finish the quarterly report by Friday", "action-item"),
    ("Schedule a meeting with John for next week", "action-item"),
    ("Let's plan to review the PR this afternoon", "action-item"),
    ("Draft an email to the client about the delay", "action-item"),
    ("Create a new Jira ticket for the login bug", "action-item"),
    ("Where do I have to go for the meeting?", "action-item"),
    ("Fix the bugs in the integration pipeline", "action-item"),
    ("Deploy the new microservice", "action-item"),
    ("Update the database schema", "action-item"),
    ("I have to go to the store", "action-item"),
    ("What are my tasks for today?", "action-item"),

    # small-talk
    ("What's the weather like?", "small-talk"),
    ("How are you doing today?", "small-talk"),
    ("Did you watch the game last night?", "small-talk"),
    ("I love eating pizza on Fridays.", "small-talk"),
    ("Tell me a joke.", "small-talk"),
    ("Hello there!", "small-talk"),
    ("Good morning", "small-talk"),
    ("How's it going?", "small-talk"),
    ("What are you up to?", "small-talk"),
    ("I like playing video games", "small-talk"),
    ("Where are you from?", "small-talk"),

    # unknown
    ("This is just random text.", "unknown"),
    ("The mitochondria is the powerhouse of the cell.", "unknown"),
    ("skjdflksdjf", "unknown"),
    ("12345 67890", "unknown"),
    ("Blue is a color.", "unknown"),
    ("The cat sat on the mat", "unknown"),
    ("I like trains", "unknown"),
    ("Testing 1 2 3", "unknown"),
    ("apples and oranges", "unknown"),
    ("qwertyuiop", "unknown")
]

MODEL_PATH = "intent_classifier.joblib"

def train_classifier(data: Optional[List[Tuple[str, str]]] = None, model_path: str = MODEL_PATH):
    """Trains a lightweight Tfidf + LogisticRegression pipeline."""
    print("Training the offline intent classifier...")
    if data is None:
        data = TRAINING_DATA
    X, y = zip(*data)
    
    # We use a TfidfVectorizer coupled with a LogisticRegression model.
    # This is extremely lightweight, uses negligible memory, and runs on CPU in < 1ms.
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), lowercase=True),
        LogisticRegression(C=1.0, class_weight='balanced', max_iter=1000)
    )
    
    model.fit(X, y)
    
    # Save the model
    joblib.dump(model, model_path)
    
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"Model saved to {model_path}. Size: {size_mb:.4f} MB")
    return model

def predict_intent(text: str, model_path: str = MODEL_PATH) -> Tuple[str, float, float]:
    """Loads the model and predicts the intent and confidence, measuring latency."""
    if not os.path.exists(model_path):
        train_classifier(model_path=model_path)
        
    model = joblib.load(model_path)
    
    start_time = time.perf_counter()
    pred = model.predict([text])[0]
    
    # Calculate confidence
    classes = model.classes_
    proba = model.predict_proba([text])[0]
    class_idx = list(classes).index(pred)
    confidence = proba[class_idx]
    
    if confidence < 0.25:
        pred = "unknown"
    
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    return pred, confidence, latency_ms

if __name__ == "__main__":
    # Ensure model is trained
    train_classifier()
    
    # Test cases to demonstrate CPU performance and offline capability
    test_queries = [
        "Please remind me to take out the trash",
        "I'm feeling really anxious about my exam",
        "We need to deploy the new microservice by 3 PM",
        "What is your favorite movie?",
        "Quantum physics is complicated."
    ]
    
    print("\n--- Testing Intent Classifier ---")
    for q in test_queries:
        intent, confidence, latency = predict_intent(q)
        print(f"Query: '{q}'")
        print(f"  -> Intent: {intent} (Confidence: {confidence:.2f}, Latency: {latency:.2f} ms)\n")
