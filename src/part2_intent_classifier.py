import time
import os
import joblib
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
    
    # emotional-support
    ("I'm feeling really sad today and I don't know why", "emotional-support"),
    ("Can you just listen to me? I had a terrible day.", "emotional-support"),
    ("I'm feeling so overwhelmed and stressed out.", "emotional-support"),
    ("Everything is going wrong, I just need someone to talk to.", "emotional-support"),
    ("I feel lonely.", "emotional-support"),

    # action-item
    ("I need to finish the quarterly report by Friday", "action-item"),
    ("Schedule a meeting with John for next week", "action-item"),
    ("Let's plan to review the PR this afternoon", "action-item"),
    ("Draft an email to the client about the delay", "action-item"),
    ("Create a new Jira ticket for the login bug", "action-item"),

    # small-talk
    ("What's the weather like?", "small-talk"),
    ("How are you doing today?", "small-talk"),
    ("Did you watch the game last night?", "small-talk"),
    ("I love eating pizza on Fridays.", "small-talk"),
    ("Tell me a joke.", "small-talk"),

    # unknown
    ("This is just random text.", "unknown"),
    ("The mitochondria is the powerhouse of the cell.", "unknown"),
    ("skjdflksdjf", "unknown"),
    ("12345 67890", "unknown"),
    ("Blue is a color.", "unknown"),
]

MODEL_PATH = "intent_classifier.joblib"

def train_classifier():
    """Trains a lightweight Tfidf + LogisticRegression pipeline."""
    print("Training the offline intent classifier...")
    X, y = zip(*TRAINING_DATA)
    
    # We use a TfidfVectorizer coupled with a LogisticRegression model.
    # This is extremely lightweight, uses negligible memory, and runs on CPU in < 1ms.
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), lowercase=True),
        LogisticRegression(C=1.0, class_weight='balanced', max_iter=1000)
    )
    
    model.fit(X, y)
    
    # Save the model
    joblib.dump(model, MODEL_PATH)
    
    size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"Model saved to {MODEL_PATH}. Size: {size_mb:.4f} MB")
    return model

def predict_intent(text: str):
    """Loads the model and predicts the intent, measuring latency."""
    if not os.path.exists(MODEL_PATH):
        train_classifier()
        
    model = joblib.load(MODEL_PATH)
    
    start_time = time.perf_counter()
    pred = model.predict([text])[0]
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    return pred, latency_ms

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
        intent, latency = predict_intent(q)
        print(f"Query: '{q}'")
        print(f"  -> Intent: {intent} (Latency: {latency:.2f} ms)\n")
