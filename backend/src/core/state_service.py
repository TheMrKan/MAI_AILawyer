import secrets
import time
from typing import Dict


class StateService:
    def __init__(self, ttl: int = 600):
        self.ttl = ttl
        self.states: Dict[str, float] = {}

    def generate_state(self) -> str:
        state = secrets.token_urlsafe(32)
        self.states[state] = time.time()
        return state

    def validate_state(self, state: str) -> bool:
        if state not in self.states:
            return False

        created_time = self.states[state]
        if time.time() - created_time >= self.ttl:
            del self.states[state]
            return False

        del self.states[state]
        return True

    def cleanup_expired(self):
        current_time = time.time()
        expired_states = [
            state for state, created_time in self.states.items()
            if current_time - created_time > self.ttl
        ]
        for state in expired_states:
            del self.states[state]


state_service = StateService()