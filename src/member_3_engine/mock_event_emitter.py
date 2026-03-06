"""
Mock Event Emitter - Member 3
Provides mock events for UI testing (Member 4) without backend
"""
import time
import threading


class MockEventEmitter:
    """
    Mock event emitter for UI development
    Simulates streaming recognition events
    """
    
    def __init__(self):
        """Initialize mock event emitter"""
        self.callbacks = {
            "on_partial": None,
            "on_final": None,
            "on_session_end": None
        }
        self.is_running = False
        self.thread = None
    
    def on_partial(self, callback):
        """Register callback for partial results"""
        self.callbacks["on_partial"] = callback
    
    def on_final(self, callback):
        """Register callback for final results"""
        self.callbacks["on_final"] = callback
    
    def on_session_end(self, callback):
        """Register callback for session end"""
        self.callbacks["on_session_end"] = callback
    
    def start_mock_session(self):
        """Start a mock recognition session"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._simulate_recognition)
        self.thread.start()
    
    def stop_mock_session(self):
        """Stop the mock session"""
        self.is_running = False
        if self.thread:
            self.thread.join()
    
    def _simulate_recognition(self):
        """Simulate streaming recognition with mock data"""
        mock_phrases = [
            "یہ ایک",
            "یہ ایک ٹیسٹ",
            "یہ ایک ٹیسٹ ہے",
        ]
        
        # Simulate partial results
        for phrase in mock_phrases:
            if not self.is_running:
                break
            
            if self.callbacks["on_partial"]:
                self.callbacks["on_partial"](phrase)
            
            time.sleep(0.5)
        
        # Simulate final result
        if self.is_running and self.callbacks["on_final"]:
            final_text = "یہ ایک ٹیسٹ ہے"
            self.callbacks["on_final"](final_text)
        
        time.sleep(0.3)
        
        # Simulate session end
        if self.is_running and self.callbacks["on_session_end"]:
            summary = {
                "recognized_text": "یہ ایک ٹیسٹ ہے",
                "total_processing_time_ms": 1500
            }
            self.callbacks["on_session_end"](summary)
        
        self.is_running = False


# Example usage for Member 4
if __name__ == "__main__":
    emitter = MockEventEmitter()
    
    # Register callbacks
    emitter.on_partial(lambda text: print(f"[Partial] {text}"))
    emitter.on_final(lambda text: print(f"[Final] {text}"))
    emitter.on_session_end(lambda summary: print(f"[Session End] {summary}"))
    
    # Start mock session
    print("Starting mock session...")
    emitter.start_mock_session()
    
    # Wait for completion
    time.sleep(3)
    print("Mock session completed")
