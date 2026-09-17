"""Bounded in-memory, session-level behavioral anomaly detection."""
from collections import defaultdict, deque
from time import monotonic
from typing import Deque, Dict

class BehavioralAnomalyEngine:
    """Detect bursts and repeated high-risk requests without retaining prompts."""
    def __init__(self, window_seconds: int = 300, max_events: int = 30):
        self.window_seconds, self.max_events = window_seconds, max_events
        self._sessions: Dict[str, Deque[Dict[str, float]]] = defaultdict(lambda: deque(maxlen=max_events))
    def evaluate(self, session_id: str, threat_score: float, similarity_score: float) -> Dict[str, object]:
        now, events = monotonic(), self._sessions[session_id]
        while events and now - events[0]["time"] > self.window_seconds:
            events.popleft()
        events.append({"time": now, "risk": max(float(threat_score), float(similarity_score))})
        high_risk_count = sum(event["risk"] >= 0.55 for event in events)
        burst, repeated = len(events) >= 8, high_risk_count >= 3
        score = min(1.0, (0.35 if burst else 0.0) + (0.65 if repeated else 0.0))
        reasons = (["High request volume in the session window."] if burst else []) + (["Repeated suspicious requests in the session window."] if repeated else [])
        return {"anomaly_score": round(score, 4), "is_anomalous": bool(reasons), "event_count": len(events), "high_risk_event_count": high_risk_count, "reasons": reasons}