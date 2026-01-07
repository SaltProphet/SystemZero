"""Mock event generator for testing."""
from typing import List, Dict, Any
import time
import random


class EventGenerator:
    """Generates realistic accessibility event sequences."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.event_id = 0
    
    def generate_window_focus(self, window_title: str) -> Dict[str, Any]:
        """Generate a window focus event."""
        self.event_id += 1
        return {
            "event_id": self.event_id,
            "type": "window_focus",
            "timestamp": time.time(),
            "window_title": window_title,
            "process": f"{window_title.lower()}_app"
        }
    
    def generate_click(self, element_name: str, element_role: str = "button") -> Dict[str, Any]:
        """Generate an element click event."""
        self.event_id += 1
        return {
            "event_id": self.event_id,
            "type": "element_click",
            "timestamp": time.time(),
            "element": {
                "name": element_name,
                "role": element_role
            }
        }
    
    def generate_text_input(self, element_name: str, text: str) -> Dict[str, Any]:
        """Generate a text input event."""
        self.event_id += 1
        return {
            "event_id": self.event_id,
            "type": "text_input",
            "timestamp": time.time(),
            "element": {
                "name": element_name,
                "role": "textbox"
            },
            "text": text
        }
    
    def generate_transition(self, from_screen: str, to_screen: str) -> Dict[str, Any]:
        """Generate a screen transition event."""
        self.event_id += 1
        return {
            "event_id": self.event_id,
            "type": "screen_transition",
            "timestamp": time.time(),
            "from_screen": from_screen,
            "to_screen": to_screen
        }
    
    def generate_sequence(self, sequence_type: str = "login_flow") -> List[Dict[str, Any]]:
        """Generate a pre-defined event sequence.
        
        Args:
            sequence_type: Type of sequence (login_flow, chat_flow, etc.)
            
        Returns:
            List of events
        """
        if sequence_type == "login_flow":
            return [
                self.generate_window_focus("Login"),
                self.generate_text_input("username", "testuser"),
                self.generate_text_input("password", "********"),
                self.generate_click("login_button"),
                self.generate_transition("login_form", "dashboard")
            ]
        elif sequence_type == "chat_flow":
            return [
                self.generate_window_focus("Discord"),
                self.generate_click("server_1", "button"),
                self.generate_click("channel_general", "button"),
                self.generate_text_input("input_box", "Hello world"),
                self.generate_click("send_button")
            ]
        elif sequence_type == "drift_injection":
            return [
                self.generate_window_focus("Normal App"),
                self.generate_click("feature_button"),
                self.generate_transition("normal_screen", "manipulative_upsell"),
                self.generate_click("decline_button"),
                self.generate_transition("manipulative_upsell", "normal_screen")
            ]
        else:
            return []
    
    def generate_random_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate random events for testing."""
        events = []
        event_types = ['window_focus', 'element_click', 'text_input']
        
        for _ in range(count):
            event_type = random.choice(event_types)
            if event_type == 'window_focus':
                events.append(self.generate_window_focus(f"App_{random.randint(1,5)}"))
            elif event_type == 'element_click':
                events.append(self.generate_click(f"button_{random.randint(1,10)}"))
            else:
                events.append(self.generate_text_input(f"input_{random.randint(1,3)}", "test text"))
        
        return events
