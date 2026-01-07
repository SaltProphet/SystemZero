"""Tests for accessibility layer."""
import pytest
import time
from core.accessibility import EventStream, TreeCapture, AccessibilityListener


class TestEventStream:
    """Test EventStream functionality."""
    
    def test_create_stream(self):
        """Test creating an event stream."""
        stream = EventStream()
        assert stream is not None
    
    def test_push_event(self):
        """Test pushing events to stream."""
        stream = EventStream(maxlen=10)
        stream.push({"type": "test", "data": "value"})
        recent = stream.get_recent(1)
        assert len(recent) == 1
        assert recent[0]["type"] == "test"
    
    def test_subscribe_callback(self):
        """Test subscribing to events."""
        stream = EventStream()
        received = []
        
        def callback(event):
            received.append(event)
        
        stream.subscribe(callback)
        stream.push({"type": "test"})
        
        time.sleep(0.1)  # Give callback time to execute
        assert len(received) == 1
    
    def test_maxlen_limit(self):
        """Test that stream respects maxlen."""
        stream = EventStream(maxlen=5)
        for i in range(10):
            stream.push({"id": i})
        
        recent = stream.get_recent(10)
        assert len(recent) <= 5
    
    def test_clear(self):
        """Test clearing the stream."""
        stream = EventStream()
        stream.push({"type": "test"})
        stream.clear()
        assert len(stream.get_recent(10)) == 0


class TestTreeCapture:
    """Test TreeCapture functionality."""
    
    def test_capture_returns_dict(self):
        """Test that capture returns a dictionary."""
        capture = TreeCapture()
        tree = capture.capture()
        assert isinstance(tree, dict)
    
    def test_capture_has_required_keys(self):
        """Test that captured tree has required keys."""
        capture = TreeCapture()
        tree = capture.capture()
        assert "timestamp" in tree
        assert "platform" in tree
        assert "active_window" in tree
        assert "root" in tree
    
    def test_capture_platform(self):
        """Test that platform is detected."""
        capture = TreeCapture()
        tree = capture.capture()
        assert tree["platform"] in ["Linux", "Darwin", "Windows"]
    
    def test_multiple_captures(self):
        """Test multiple sequential captures."""
        capture = TreeCapture()
        tree1 = capture.capture()
        time.sleep(0.01)
        tree2 = capture.capture()
        # Timestamps should differ
        assert tree1["timestamp"] != tree2["timestamp"]


class TestAccessibilityListener:
    """Test AccessibilityListener functionality."""
    
    def test_create_listener(self):
        """Test creating a listener."""
        stream = EventStream()
        listener = AccessibilityListener(stream)
        assert listener is not None
    
    def test_listener_has_stream(self):
        """Test that listener has event stream."""
        stream = EventStream()
        listener = AccessibilityListener(stream)
        assert listener.event_stream is stream
    
    def test_on_event(self):
        """Test on_event processes events."""
        stream = EventStream()
        listener = AccessibilityListener(stream)
        
        raw_event = {"type": "window_focus", "window": "Test"}
        listener.on_event(raw_event)
        
        recent = stream.get_recent(1)
        assert len(recent) == 1
        assert recent[0]["data"]["type"] == "window_focus"
    
    def test_start_stop(self):
        """Test starting and stopping listener."""
        stream = EventStream()
        listener = AccessibilityListener(stream, poll_interval=0.1)
        
        listener.start()
        time.sleep(0.3)  # Let it run
        listener.stop()
        
        # Should have generated some mock events
        recent = stream.get_recent(10)
        assert len(recent) > 0
    
    def test_set_callback(self):
        """Test setting custom callback."""
        stream = EventStream()
        listener = AccessibilityListener(stream)
        
        called = []
        def callback(event):
            called.append(event)
        
        listener.set_callback(callback)
        listener.on_event({"type": "test"})
        
        time.sleep(0.1)
        assert len(called) == 1
