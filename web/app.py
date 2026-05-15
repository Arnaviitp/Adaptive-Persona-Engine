from flask import Flask, render_template, request, jsonify
import sys
import os

# Add src to path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from part1_drift_detector import PersonaDriftDetector
from part2_intent_classifier import predict_intent
from part3_rag_resolver import RAGConflictResolver

app = Flask(__name__)

detector = PersonaDriftDetector()
resolver = RAGConflictResolver()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/drift', methods=['POST'])
def drift():
    data = request.json
    logs = data.get('logs', [])
    timeline = detector.analyze_drift(logs)
    return jsonify({"timeline": timeline})

@app.route('/api/intent', methods=['POST'])
def intent():
    data = request.json
    text = data.get('text', '')
    # predict_intent uses the trained joblib model
    # Note: ensure that we change directory or the joblib path is absolute if there are issues
    # But since predict_intent uses relative path, let's run app.py from the root of the project ideally, or web/
    
    # Actually, part2 has `MODEL_PATH = "intent_classifier.joblib"` which will be in the cwd.
    intent_class, confidence, latency = predict_intent(text)
    return jsonify({"intent": intent_class, "confidence": confidence, "latency": latency})

@app.route('/api/resolve', methods=['POST'])
def resolve():
    data = request.json
    query = data.get('query', '')
    chunks = data.get('chunks', [])
    result = resolver.resolve(query, chunks)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
