"""
Session Controller - Member 3
Manages session lifecycle: initialization, start, stop, state, timing
"""
import time


class SessionController:
    """
    Controls STT session lifecycle and state management
    """
    
    def __init__(self, streaming_engine, audio_capture):
        """
        Initialize session controller
        
        Args:
            streaming_engine: StreamingEngine instance
            audio_capture: AudioCapture instance from Member 2
        """
        self.streaming_engine = streaming_engine
        self.audio_capture = audio_capture
        
        # Session state
        self.is_active = False
        self.session_start_time = None
        self.session_end_time = None
    
    def initialize(self):
        """
        Initialize the session controller
        Prepares all components for session start
        """
        print("[SessionController] Initialized")
        return True
    
    def start_session(self):
        """
        Start a new STT session
        Starts audio capture and streaming engine
        """
        if self.is_active:
            print("[SessionController] Session already active")
            return False
        
        try:
            # Record start time
            self.session_start_time = time.time()
            self.session_end_time = None
            
            # Start audio capture
            self.audio_capture.start_stream()
            
            # Start streaming engine
            self.streaming_engine.start()
            
            self.is_active = True
            print("[SessionController] Session started")
            return True
        
        except Exception as e:
            print(f"[SessionController] Failed to start session: {e}")
            self.is_active = False
            return False
    
    def stop_session(self):
        """
        Stop the current STT session
        Stops audio capture and streaming engine
        """
        if not self.is_active:
            print("[SessionController] No active session to stop")
            return False
        
        try:
            # Stop audio capture first
            self.audio_capture.stop_stream()
            
            # Stop streaming engine
            self.streaming_engine.stop()
            
            # Record end time
            self.session_end_time = time.time()
            self.is_active = False
            
            print("[SessionController] Session stopped")
            return True
        
        except Exception as e:
            print(f"[SessionController] Error stopping session: {e}")
            return False
    
    def get_session_state(self):
        """
        Get current session state
        
        Returns:
            Dict with session state information
        """
        state = {
            "is_active": self.is_active,
            "start_time": self.session_start_time,
            "end_time": self.session_end_time
        }
        
        if self.is_active and self.session_start_time:
            state["elapsed_time_ms"] = int((time.time() - self.session_start_time) * 1000)
        elif self.session_start_time and self.session_end_time:
            state["total_time_ms"] = int((self.session_end_time - self.session_start_time) * 1000)
        
        return state
    
    def get_elapsed_time(self):
        """
        Get elapsed time since session start in milliseconds
        
        Returns:
            Elapsed time in ms, or 0 if no active session
        """
        if not self.is_active or not self.session_start_time:
            return 0
        
        return int((time.time() - self.session_start_time) * 1000)
    
    def is_session_active(self):
        """Check if session is currently active"""
        return self.is_active
