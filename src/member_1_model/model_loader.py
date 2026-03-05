import whisper
import numpy as np

class ModelLoader:
    def __init__(self):
        self.model = None
        self.sample_rate = 16000
        self.language = "ur"

    def loadModel(self, config):
        try:
            model_name = config.get("model_name", "base")
            self.sample_rate = config.get("sample_rate", 16000)
            self.language = config.get("language", "ur")
            
            print(f"Loading Whisper Model: {model_name}...")
            self.model = whisper.load_model(model_name)
            print("Model Loaded Successfully")
            return True
        except Exception as e:
            print("Model loading failed:", e)
            return False

    def recognize(self, audio_chunk):
        try:
            audio_np = np.frombuffer(audio_chunk, np.int16).astype(np.float32) / 32768.0
            result = self.model.transcribe(audio_np, language=self.language, fp16=False)
            return {"partial": "", "final": result["text"]}
        except Exception as e:
            print("Recognition error:", e)
            return {"partial": "", "final": ""}