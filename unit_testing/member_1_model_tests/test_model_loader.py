import json
import unittest
import sys
import os

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.member_1_model.model_loader import ModelLoader

class TestModelLoader(unittest.TestCase):

    def test_model_loading(self):
        # Config path fix
        config_path = os.path.join(os.getcwd(), "config", "config.json") 
        
        with open(config_path, "r") as f:
            config = json.load(f)

        loader = ModelLoader()
        
        # Sahi method name 'loadModel' use karein
        result = loader.loadModel(config) 

        # Kyunke aapka code True return karta hai
        self.assertTrue(result, "Model load nahi ho saka!")

    def test_transcription(self):
        # Audio test (Urdu + English)
        audio_path = os.path.join("unit_testing", "member_1_model_tests", "benchmark_audio", "sample_ur_01.wav")
        
        if not os.path.exists(audio_path):
            self.fail("Audio file nahi mili!")

        loader = ModelLoader()
        # Pehle model load karein
        loader.loadModel({"model_name": "base", "language": "ur"})
        
        # Whisper direct file bhi leta hai, 
        # lekin aapka 'recognize' chunk leta hai. 
        # Direct test ke liye hum whisper use kar lete hain:
        import whisper
        model = loader.model # Loader ke andar se model nikalein
        
        print("\n--- Urdu Result ---")
        res_ur = model.transcribe(audio_path)
        print(res_ur["text"])
        
        print("\n--- English Result ---")
        res_en = model.transcribe(audio_path, task="translate")
        print(res_en["text"])

        self.assertIsNotNone(res_ur["text"])

if __name__ == "__main__":
    unittest.main()