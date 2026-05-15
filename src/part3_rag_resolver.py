import time
import json

class RAGConflictResolver:
    def __init__(self, recency_weight=0.6, emotion_weight=0.4):
        self.recency_weight = recency_weight
        self.emotion_weight = emotion_weight

    def _calculate_recency_score(self, current_time, chunk_time, max_age):
        """Calculates a normalized recency score (0.0 to 1.0)."""
        age = current_time - chunk_time
        if age < 0:
            return 1.0
        if age >= max_age:
            return 0.0
        return 1.0 - (age / max_age)

    def rank_chunks(self, chunks: list) -> list:
        """
        Ranks chunks based on recency and emotional weight.
        Expected chunk format: {"text": str, "timestamp": int, "emotion_weight": float}
        """
        if not chunks:
            return []

        current_time = max(chunk['timestamp'] for chunk in chunks)
        # Assume max age is the difference between oldest and newest chunk + 1
        min_time = min(chunk['timestamp'] for chunk in chunks)
        max_age = max((current_time - min_time), 1)

        ranked = []
        for chunk in chunks:
            recency_score = self._calculate_recency_score(current_time, chunk['timestamp'], max_age)
            # Emotion weight is assumed to be provided by an upstream classifier (0.0 to 1.0)
            emotion_score = chunk.get('emotion_weight', 0.5)
            
            final_score = (self.recency_weight * recency_score) + (self.emotion_weight * emotion_score)
            
            chunk_copy = chunk.copy()
            chunk_copy['recency_score'] = recency_score
            chunk_copy['final_score'] = final_score
            ranked.append(chunk_copy)
            
        ranked.sort(key=lambda x: x['final_score'], reverse=True)
        return ranked

    def flag_contradictions(self, chunks: list) -> list:
        """
        Flags contradictions among the top chunks.
        In a real scenario, an LLM or NLI (Natural Language Inference) model would be used here.
        We will use a mock LLM logic here to simulate contradiction detection.
        """
        # Simulated LLM logic: For demonstration, we assume chunks contain conflicting info 
        # about the "sister" and we identify them.
        contradictions = []
        texts = [c['text'].lower() for c in chunks]
        
        # Simple heuristic for mock
        if any("don't like" in t or "hates" in t for t in texts) and any("loves" in t or "best friend" in t for t in texts):
            contradictions.append("Conflicting emotions or relationships regarding the sister.")
        if any("only child" in t for t in texts) and any("sister" in t for t in texts):
            contradictions.append("Conflict regarding existence of a sister.")
            
        return contradictions

    def generate_merged_answer(self, query: str, ranked_chunks: list, contradictions: list) -> str:
        """
        Uses an LLM to generate a merged coherent answer based on ranked chunks and flagged contradictions.
        """
        prompt = f"""
        Query: {query}
        
        Ranked Context Chunks (highest priority first):
        {json.dumps([c['text'] for c in ranked_chunks], indent=2)}
        
        Known Contradictions:
        {json.dumps(contradictions, indent=2)}
        
        Task: Provide a coherent answer that addresses the query. 
        Acknowledge the conflicting information but weigh the more recent and emotionally significant context heavier.
        """
        
        # Mock LLM response
        return "Based on your history, you used to mention not getting along with your sister, but in your most recent and emotionally charged entries, you mentioned that she is your best friend and you love her. So, it seems your relationship with your sister has significantly improved recently."

    def resolve(self, query: str, retrieved_chunks: list) -> dict:
        ranked_chunks = self.rank_chunks(retrieved_chunks)
        contradictions = self.flag_contradictions(ranked_chunks)
        answer = self.generate_merged_answer(query, ranked_chunks, contradictions)
        
        return {
            "ranked_chunks": ranked_chunks,
            "contradictions": contradictions,
            "merged_answer": answer
        }

if __name__ == "__main__":
    # Example hard retrieval problem chunks
    # timestamp could be days since epoch
    chunks = [
        {"id": 1, "text": "I really don't like my sister. We always fight.", "timestamp": 10, "emotion_weight": 0.6},
        {"id": 2, "text": "My sister and I are going to a concert.", "timestamp": 20, "emotion_weight": 0.3},
        {"id": 3, "text": "My sister has been my best friend lately. I love her so much.", "timestamp": 30, "emotion_weight": 0.9}
    ]
    
    query = "Did I mention anything about my sister?"
    
    resolver = RAGConflictResolver(recency_weight=0.5, emotion_weight=0.5)
    print(f"Query: {query}\n")
    
    result = resolver.resolve(query, chunks)
    
    print("--- Ranked Chunks ---")
    for i, chunk in enumerate(result['ranked_chunks']):
        print(f"{i+1}. Score: {chunk['final_score']:.2f} | Text: {chunk['text']}")
        
    print("\n--- Flagged Contradictions ---")
    for c in result['contradictions']:
        print(f"- {c}")
        
    print("\n--- Merged Coherent Answer ---")
    print(result['merged_answer'])
