from backend.app.core.config import Settings, settings
from backend.app.services.state_store import StateStore, state_store

def get_settings() -> Settings:
    return settings

def get_state_store() -> StateStore:
    return state_store
