"""Pre-built event sequences for testing."""
from .event_generator import EventGenerator

# Initialize generator
gen = EventGenerator()

# Normal user login flow
LOGIN_SEQUENCE = gen.generate_sequence("login_flow")

# Chat interaction flow
CHAT_SEQUENCE = gen.generate_sequence("chat_flow")

# Drift injection sequence (normal → manipulative → normal)
DRIFT_INJECTION_SEQUENCE = gen.generate_sequence("drift_injection")

# Invalid transition sequence (should trigger drift)
INVALID_TRANSITION_SEQUENCE = [
    gen.generate_window_focus("Discord"),
    gen.generate_transition("discord_chat", "doordash_offer"),  # Invalid!
    gen.generate_click("accept_button")
]

# Long random sequence for stress testing
STRESS_TEST_SEQUENCE = gen.generate_random_events(100)
