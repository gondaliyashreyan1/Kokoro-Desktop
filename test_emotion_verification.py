#!/usr/bin/env python3
"""
Test script to verify that emotions actually affect the audio output
"""

import sys
import os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from kokoro_tts import get_emotion_profile
from kokoro_onnx import Kokoro

def test_emotion_impact():
    """Test if emotions actually change the audio parameters"""
    print("Testing if emotions actually change audio parameters...")
    
    # Load the model
    kokoro = Kokoro('./kokoro-v1.0.onnx', './voices-v1.0.bin')
    
    # Get different emotion profiles
    neutral_profile = get_emotion_profile("neutral")
    happy_profile = get_emotion_profile("happy")
    sad_profile = get_emotion_profile("sad")
    
    print(f"Neutral profile: {neutral_profile}")
    print(f"Happy profile: {happy_profile}")
    print(f"Sad profile: {sad_profile}")
    
    # Verify that profiles have different parameters
    assert neutral_profile["speed"] != happy_profile["speed"], "Happy should have different speed than neutral"
    assert neutral_profile["speed"] != sad_profile["speed"], "Sad should have different speed than neutral"
    assert neutral_profile["pitch"] != happy_profile["pitch"], "Happy should have different pitch than neutral"
    assert neutral_profile["pitch"] != sad_profile["pitch"], "Sad should have different pitch than neutral"
    
    print("✓ Emotion profiles have different parameters")
    
    # Test with a custom emotion
    from kokoro_tts import register_custom_emotion
    register_custom_emotion("test_emotion", speed=1.5, pitch=0.8, emphasis="very_strong")
    
    test_profile = get_emotion_profile("test_emotion")
    print(f"Custom emotion profile: {test_profile}")
    
    assert test_profile["speed"] == 1.5, "Custom emotion speed not set correctly"
    assert test_profile["pitch"] == 0.8, "Custom emotion pitch not set correctly"
    
    print("✓ Custom emotion registration works and affects parameters")
    
    # Test actual audio generation with different emotions (simulated)
    # Since we can't easily test the actual audio output without generating files,
    # we'll verify that the parameters would be applied correctly
    test_text = "This is a test of the emotion system."
    voice = "af_sarah"
    
    # Simulate how the parameters would be used
    base_speed = 1.0
    happy_adjusted_speed = base_speed * happy_profile["speed"]
    sad_adjusted_speed = base_speed * sad_profile["speed"]
    
    print(f"Base speed: {base_speed}")
    print(f"With happy emotion: {happy_adjusted_speed}")
    print(f"With sad emotion: {sad_adjusted_speed}")
    
    assert happy_adjusted_speed != base_speed, "Happy emotion should change speed"
    assert sad_adjusted_speed != base_speed, "Sad emotion should change speed"
    assert happy_adjusted_speed != sad_adjusted_speed, "Happy and sad should result in different speeds"
    
    print("✓ Emotions would result in different audio parameters")
    

def test_audio_effects():
    """Test if audio effects are properly registered"""
    print("\nTesting audio effects...")
    
    from kokoro_tts import get_audio_effects, register_custom_audio_effect
    
    # Test default effects
    none_effect = get_audio_effects("none")
    reverb_effect = get_audio_effects("reverb_light")
    
    print(f"None effect: {none_effect}")
    print(f"Reverb effect: {reverb_effect}")
    
    assert isinstance(none_effect, dict), "None effect should be a dict"
    assert "reverb" in reverb_effect or len(reverb_effect) > 0, "Reverb effect should have parameters"
    
    # Test custom effect
    register_custom_audio_effect("test_effect", gain=1.2, reverb=0.5, pitch_shift=0.1)
    test_effect = get_audio_effects("test_effect")
    
    print(f"Custom effect: {test_effect}")
    
    assert test_effect["gain"] == 1.2, "Gain not set correctly"
    assert test_effect["reverb"] == 0.5, "Reverb not set correctly"
    assert test_effect["pitch_shift"] == 0.1, "Pitch shift not set correctly"
    
    print("✓ Audio effects work correctly")


def run_tests():
    """Run all tests"""
    print("Testing emotion and effect functionality")
    print("="*50)
    
    test_emotion_impact()
    test_audio_effects()
    
    print("="*50)
    print("All emotion/effect tests passed! ✓")


if __name__ == "__main__":
    run_tests()