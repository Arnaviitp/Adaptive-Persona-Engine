const defaultLogs = [
    {"day": 1, "messages": ["Hello, I would like to inquire about the project constraints.", "Could you provide the documentation?"]},
    {"day": 4, "messages": ["Man, this is so annoying. The React errors keep popping up.", "I've been debugging for hours."]},
    {"day": 7, "messages": ["Finally got it working! Haha, time to celebrate.", "Going to my sister's birthday party now!"]}
];

const defaultChunks = [
    {"id": 1, "text": "I really don't like my sister. We always fight.", "timestamp": 10, "emotion_weight": 0.6},
    {"id": 2, "text": "My sister and I are going to a concert.", "timestamp": 20, "emotion_weight": 0.3},
    {"id": 3, "text": "My sister has been my best friend lately. I love her so much.", "timestamp": 30, "emotion_weight": 0.9}
];

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('drift-input').value = JSON.stringify(defaultLogs, null, 2);
    document.getElementById('rag-chunks').value = JSON.stringify(defaultChunks, null, 2);
});

async function analyzeDrift() {
    const inputStr = document.getElementById('drift-input').value;
    const outputEl = document.getElementById('drift-output');
    
    try {
        const logs = JSON.parse(inputStr);
        outputEl.innerHTML = 'Analyzing...';
        outputEl.classList.add('show');
        
        const res = await fetch('/api/drift', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ logs })
        });
        
        const data = await res.json();
        if (data.timeline) {
            let html = '<strong>Drift Timeline:</strong><br><br>';
            data.timeline.forEach(item => {
                html += `Day ${item.day} &rarr; <span style="color:#60a5fa">${item.mood_tone}</span><br>`;
                html += `<small style="color:#94a3b8">Trigger: ${item.trigger}</small><br><br>`;
            });
            outputEl.innerHTML = html;
        } else {
            outputEl.textContent = JSON.stringify(data, null, 2);
        }
    } catch (e) {
        outputEl.textContent = 'Error: Invalid JSON or Server Error\n' + e.message;
        outputEl.classList.add('show');
    }
}

async function classifyIntent() {
    const text = document.getElementById('intent-input').value;
    const outputEl = document.getElementById('intent-output');
    
    if (!text) {
        outputEl.textContent = 'Please enter some text.';
        outputEl.classList.add('show');
        return;
    }
    
    outputEl.innerHTML = 'Classifying...';
    outputEl.classList.add('show');
    
    try {
        const res = await fetch('/api/intent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        const data = await res.json();
        outputEl.innerHTML = `<strong>Intent:</strong> <span style="color:#34d399">${data.intent}</span><br><strong>Confidence:</strong> ${(data.confidence || 0).toFixed(2)}<br><strong>Latency:</strong> ${data.latency.toFixed(2)} ms`;
    } catch (e) {
        outputEl.textContent = 'Error: ' + e.message;
    }
}

async function resolveConflict() {
    const query = document.getElementById('rag-query').value || "Did I mention anything about my sister?";
    const chunksStr = document.getElementById('rag-chunks').value;
    const outputEl = document.getElementById('rag-output');
    
    try {
        const chunks = JSON.parse(chunksStr);
        outputEl.innerHTML = 'Resolving...';
        outputEl.classList.add('show');
        
        const res = await fetch('/api/resolve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, chunks })
        });
        
        const data = await res.json();
        
        let html = `<strong>Merged Answer:</strong><br><span style="color:#a78bfa">${data.merged_answer}</span><br><br>`;
        html += `<strong>Contradictions Flagged:</strong><br>`;
        if (data.contradictions.length > 0) {
            data.contradictions.forEach(c => html += `- ${c}<br>`);
        } else {
            html += `None<br>`;
        }
        
        html += `<br><strong>Ranked Chunks (Top 3):</strong><br>`;
        data.ranked_chunks.slice(0, 3).forEach((c, i) => {
            html += `${i+1}. [Score: ${c.final_score.toFixed(2)}] ${c.text}<br>`;
        });
        
        outputEl.innerHTML = html;
        
    } catch (e) {
        outputEl.textContent = 'Error: Invalid JSON or Server Error\n' + e.message;
        outputEl.classList.add('show');
    }
}
