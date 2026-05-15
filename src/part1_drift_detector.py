import json
import re
from typing import List, Dict, Any

class PersonaDriftDetector:
    def __init__(self):
        # We define a prompt template that an LLM would use to extract drift.
        self.prompt_template = """
        You are a Persona Drift Detector. 
        Analyze the following daily user logs and track how the user's mood and tone change across days.
        
        For each day, identify:
        1. The primary mood/tone.
        2. The trigger that caused any drift or shift in tone (can be a topic, event, or person mentioned).
        
        Input Logs:
        {logs}
        
        Output as a JSON list of objects with keys: "day", "mood_tone", "trigger".
        """

    def _call_llm(self, prompt: str) -> str:
        """
        Mock LLM call. In a real scenario, you would use google.generativeai or openai here.
        This mock returns a realistic simulated response for the example data.
        """
        # Simulated response based on the expected example data
        simulated_response = [
            {
                "day": 1,
                "mood_tone": "curious & formal",
                "trigger": "Initial interaction, asking about project constraints"
            },
            {
                "day": 4,
                "mood_tone": "casual & frustrated",
                "trigger": "Bugs in the integration pipeline, mentioned 'React errors'"
            },
            {
                "day": 7,
                "mood_tone": "playful & relieved",
                "trigger": "Sister's birthday party, successful deployment"
            }
        ]
        return json.dumps(simulated_response)

    def analyze_drift(self, user_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes the user logs to detect persona drift across days.
        Returns a list of dictionaries containing the timeline of drifts and triggers.
        """
        logs_str = json.dumps(user_logs, indent=2)
        prompt = self.prompt_template.format(logs=logs_str)
        
        # Here we would call the actual LLM API
        response_text = self._call_llm(prompt)
        
        # Extract JSON using regex in case of markdown wrapping or extra text
        match = re.search(r"\[.*\]", response_text, re.DOTALL)
        json_str = match.group(0) if match else response_text
        
        try:
            timeline = json.loads(json_str)
            return timeline
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON.")
            return []

    def format_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        """Formats the timeline into a readable string representation."""
        output = []
        for entry in timeline:
            day = entry.get("day", "Unknown Day")
            mood = entry.get("mood_tone", "Unknown Tone")
            trigger = entry.get("trigger", "Unknown Trigger")
            output.append(f"Day {day} -> {mood} (Trigger: {trigger})")
        return "\n".join(output)

if __name__ == "__main__":
    # Example "Round 1" persona or chat logs
    sample_logs = [
        {"day": 1, "messages": ["Hello, I would like to inquire about the project constraints.", "Could you provide the documentation?"]},
        {"day": 4, "messages": ["Man, this is so annoying. The React errors keep popping up.", "I've been debugging for hours."]},
        {"day": 7, "messages": ["Finally got it working! Haha, time to celebrate.", "Going to my sister's birthday party now!"]}
    ]
    
    detector = PersonaDriftDetector()
    print("Analyzing user logs for persona drift...\n")
    timeline = detector.analyze_drift(sample_logs)
    
    formatted_output = detector.format_timeline(timeline)
    print("--- Drift Timeline ---")
    print(formatted_output)
