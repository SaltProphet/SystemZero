class AccessibilityListener:
    def __init__(self, event_stream): self.event_stream = event_stream
    def start(self): pass
    def on_event(self, raw_event): self.event_stream.push(raw_event)
