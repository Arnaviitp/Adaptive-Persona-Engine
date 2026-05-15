# System Design: Sync Architecture & Data Privacy

## Overview
The **Adaptive Persona Engine** adheres to a strict "Local-First" architecture. This means the primary source of truth is the user's local device, minimizing latency and maximizing privacy. However, to support multi-device workflows (e.g., seamless transition from a mobile phone to a desktop), the system requires a robust, privacy-preserving synchronization strategy.

This document outlines the on-device storage paradigm, the data partitioning boundaries between local and cloud, and the deterministic conflict resolution mechanisms.

---

## 1. On-Device Storage
To guarantee that the user's most sensitive data is not exposed to cloud breaches, the system employs localized, sandboxed data stores:

*   **Relational Storage (SQLite + SQLCipher):** 
    Stores raw conversation transcripts, timestamps, explicitly identified triggers, and exact Named Entities (e.g., family names, specific locations). This database is encrypted at rest using AES-256.
*   **Local Vector Store (Chroma / FAISS):** 
    Stores the dense vector embeddings of the interactions. These embeddings are mathematically irreversible representations of the text, enabling offline semantic search for the RAG pipeline.
*   **Persona Timeline Database:** 
    A lightweight key-value store maintaining the temporal states of the user's mood and tone (e.g., `Day 4: Frustrated`).

By executing the **Offline Intent Classifier** directly on the CPU, raw data never has to be streamed to an external API (like OpenAI) just to determine user intent.

---

## 2. Data Partitioning: What Syncs vs. What Stays Local
The boundary between synced and local data is aggressively biased toward local retention.

### Stays Strictly Local (Never Transmitted):
*   **Raw PII Data:** Exact text transcripts, original audio files, and raw interaction logs.
*   **High-Frequency / Low-Value Actions:** Ephemeral intents (e.g., "set a timer", "turn on lights") that do not contribute to long-term persona drift.
*   **Cryptographic Keys:** Local device encryption keys remain bound to the hardware enclave.

### Synced via End-to-End Encryption (E2EE):
*   **Anonymized Semantic Vectors:** Mathematical embeddings of interactions. (If intercepted, the text cannot be reconstructed, but it allows the cloud to act as a blind vector relay between devices).
*   **Persona Drift Timelines:** The aggregated mood/tone states. This allows a desktop device to know the user had a frustrating experience on their mobile phone earlier in the day.
*   **CRDT State Vectors:** Logical timestamps and merge vectors required for conflict resolution.

*Note: All synced payloads are E2E encrypted on the client device using a user-controlled passphrase before being dispatched to the relay server.*

---

## 3. Conflict Resolution Strategy
In a local-first system, it is highly probable that a user generates data on two disconnected devices simultaneously. When both devices reconnect, their states will diverge. We resolve this using **Conflict-free Replicated Data Types (CRDTs)** combined with our **RAG Heuristic**.

### Deterministic State Merging (CRDTs)
*   **Configuration & Settings:** Resolved using a **Last-Write-Wins (LWW) Register**. Logical clocks (e.g., Hybrid Logical Clocks) ensure that the most recent configuration change across any device is respected, ignoring network latency.
*   **Interaction Logging:** Resolved using a **Grow-Only Set (G-Set)**. Interaction logs are immutable. If Device A logs an interaction and Device B logs a different interaction offline, upon sync, both interactions are appended to the global set. No data is overwritten.

### Semantic Conflict Resolution (RAG Resolver)
When a G-Set appends two contradictory interactions from different devices (e.g., Device A: "I hate React", Device B: "I love React"), standard database merging cannot determine the "correct" emotional state. 

Instead of discarding data, both vectors are synced into the local vector store. The conflict is dynamically resolved at query time by the **RAG Conflict Resolver** (Part 3). 
*   **Recency Decay:** The interaction with the newer logical timestamp is favored.
*   **Emotional Weight:** If timestamps are nearly identical, the system mathematically calculates the emotional density of the vector. The vector displaying the stronger emotional conviction anchors the generated response.
*   **Flagging:** The contradiction is explicitly flagged in the response metadata so the language model is aware the user is exhibiting volatile or conflicting states across devices.
