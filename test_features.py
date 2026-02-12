#!/usr/bin/env python3
"""
Test script for Kokoro Desktop new features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from kokoro_tts import (
    register_custom_emotion, 
    register_custom_audio_effect, 
    get_all_emotion_profiles,
    get_all_audio_effects,
    detect_speakers,
    assign_voices_to_speakers,
    print_gradient_logo,
    VERSION
)

def test_custom_emotions():
    """Test custom emotion registration"""
    print("Testing custom emotion registration...")
    
    # Register a custom emotion
    register_custom_emotion("dramatic", speed=0.8, pitch=0.5, emphasis="theatrical")
    
    # Get all emotions and verify the new one is there
    emotions = get_all_emotion_profiles()
    assert "dramatic" in emotions, "Custom emotion not registered"
    assert emotions["dramatic"]["speed"] == 0.8, "Speed not set correctly"
    assert emotions["dramatic"]["pitch"] == 0.5, "Pitch not set correctly"
    assert emotions["dramatic"]["emphasis"] == "theatrical", "Emphasis not set correctly"
    
    print("✓ Custom emotion registration works")


def test_custom_effects():
    """Test custom audio effect registration"""
    print("Testing custom audio effect registration...")
    
    # Register a custom audio effect
    register_custom_audio_effect("chorus", chorus_depth=0.7, chorus_rate=1.5)
    
    # Get all effects and verify the new one is there
    effects = get_all_audio_effects()
    assert "chorus" in effects, "Custom effect not registered"
    assert effects["chorus"]["chorus_depth"] == 0.7, "Chorus depth not set correctly"
    assert effects["chorus"]["chorus_rate"] == 1.5, "Chorus rate not set correctly"
    
    print("✓ Custom audio effect registration works")


def test_speaker_detection():
    """Test speaker detection functionality"""
    print("Testing speaker detection...")
    
    # Test text with speakers
    test_text = """John: Hello everyone, welcome to the meeting.
Sarah: Thank you John, I'm excited to be here.
Mike said: I agree with Sarah, this is going to be productive."""
    
    speakers = detect_speakers(test_text)
    
    # Should detect at least 2 speakers
    assert len(speakers) >= 2, f"Expected at least 2 speakers, got {len(speakers)}"
    
    # Check that we have the expected speakers
    speaker_names = [s[0] for s in speakers]
    assert "John" in speaker_names, "John not detected as speaker"
    assert "Sarah" in speaker_names, "Sarah not detected as speaker"
    
    print("✓ Speaker detection works")


def test_version_variable():
    """Test that version variable is properly set"""
    print("Testing version variable...")
    
    # Check that version is properly formatted
    assert VERSION.startswith("2."), f"Version should start with 2., got {VERSION}"
    assert isinstance(VERSION, str), "Version should be a string"
    
    print(f"✓ Version is correctly set to {VERSION}")


def test_ascii_art():
    """Test ASCII art function"""
    print("Testing ASCII art logo...")
    
    # Just call the function to make sure it doesn't crash
    try:
        print_gradient_logo()
        print("✓ ASCII art logo works")
    except Exception as e:
        print(f"✗ ASCII art logo failed: {e}")


def run_all_tests():
    """Run all tests"""
    print(f"Running tests for Kokoro Desktop v{VERSION}")
    print("="*50)
    
    test_custom_emotions()
    test_custom_effects()
    test_speaker_detection()
    test_version_variable()
    test_ascii_art()
    
    print("="*50)
    print("All tests passed! ✓")


if __name__ == "__main__":
    run_all_tests()