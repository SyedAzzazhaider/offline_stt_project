"""
Result Handler Module - Member 3
Handles partial and final result detection logic
"""


class ResultHandler:
    """Manages partial and final recognition results"""
    
    def __init__(self):
        """Initialize result handler"""
        self.last_partial = ""
        self.accumulated_text = ""
    
    def process_result(self, recognition_result):
        """
        Process recognition result and determine if it's partial or final
        
        Args:
            recognition_result: Dict with 'partial' and 'final' keys from model
            
        Returns:
            Dict with 'type' ('partial' or 'final') and 'text'
        """
        if not recognition_result:
            return None
        
        partial_text = recognition_result.get("partial", "").strip()
        final_text = recognition_result.get("final", "").strip()
        
        # If we have final text, it's a final result
        if final_text:
            self.accumulated_text += " " + final_text if self.accumulated_text else final_text
            self.last_partial = ""
            return {
                "type": "final",
                "text": final_text
            }
        
        # If we have partial text and it's different from last partial
        if partial_text and partial_text != self.last_partial:
            self.last_partial = partial_text
            return {
                "type": "partial",
                "text": partial_text
            }
        
        return None
    
    def get_accumulated_text(self):
        """Get all accumulated final text"""
        return self.accumulated_text
    
    def reset(self):
        """Reset handler state"""
        self.last_partial = ""
        self.accumulated_text = ""
