#!/usr/bin/env python3
"""
Comprehensive test for Kokoro Desktop API endpoints and model parameters
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from kokoro_tts import (
    register_custom_emotion, 
    register_custom_audio_effect, 
    get_all_emotion_profiles,
    get_all_audio_effects,
    get_emotion_profile,
    get_audio_effects,
    load_user_presets,
    save_user_presets,
    detect_speakers,
    assign_voices_to_speakers,
    process_multispeaker_text,
    VERSION
)
from kokoro_onnx import Kokoro

def test_api_endpoints():
    """Test the API endpoints for managing emotions and effects"""
    print("Testing API endpoints...")
    
    # Test registering custom emotions
    register_custom_emotion("heroic", speed=1.05, pitch=0.1, emphasis="bold")
    register_custom_emotion("whisper", speed=0.7, pitch=-0.2, emphasis="soft")
    
    # Test getting all emotion profiles
    emotions = get_all_emotion_profiles()
    assert "heroic" in emotions, "Heroic emotion not found"
    assert "whisper" in emotions, "Whisper emotion not found"
    assert emotions["heroic"]["speed"] == 1.05, "Heroic speed incorrect"
    assert emotions["whisper"]["emphasis"] == "soft", "Whisper emphasis incorrect"
    
    # Test getting specific emotion profile
    heroic_profile = get_emotion_profile("heroic")
    assert heroic_profile["speed"] == 1.05, "Retrieved heroic speed incorrect"
    
    # Test fallback for unknown emotion
    neutral_profile = get_emotion_profile("nonexistent")
    assert neutral_profile["emphasis"] == "normal", "Fallback profile incorrect"
    
    # Test registering custom effects
    register_custom_audio_effect("space_echo", delay=0.8, decay=0.9, mix=0.7)
    register_custom_audio_effect("vintage_radio", low_pass=2000, compression=0.9)
    
    # Test getting all audio effects
    effects = get_all_audio_effects()
    assert "space_echo" in effects, "Space echo effect not found"
    assert "vintage_radio" in effects, "Vintage radio effect not found"
    assert effects["space_echo"]["delay"] == 0.8, "Space echo delay incorrect"
    
    # Test getting specific audio effect
    space_effect = get_audio_effects("space_echo")
    assert space_effect["decay"] == 0.9, "Retrieved space echo decay incorrect"
    
    print("✓ API endpoints work correctly")


def test_preset_management():
    """Test preset save/load functionality"""
    print("Testing preset management...")
    
    # Test loading presets from non-existent file (should return empty dict)
    presets = load_user_presets()
    assert isinstance(presets, dict), "Presets should be a dict"
    
    # Test saving a preset
    test_presets = {
        "bedtime_story": {
            "voice": "af_sarah",
            "speed": 0.8,
            "emotion": "calm",
            "effect": "reverb_light"
        },
        "news_announcer": {
            "voice": "am_michael",
            "speed": 1.0,
            "emotion": "neutral",
            "effect": "none"
        }
    }
    
    # Save test presets to a temporary location
    temp_presets_file = os.path.expanduser("~/.kokoro-test-presets.json")
    original_path = os.path.expanduser("~/.kokoro-presets.json")
    
    # Temporarily change the preset file location for testing
    import kokoro_tts
    kokoro_tts.USER_PRESETS_FILE = temp_presets_file
    
    success = save_user_presets(test_presets)
    assert success, "Failed to save presets"
    
    # Load the presets back
    loaded_presets = load_user_presets()
    assert "bedtime_story" in loaded_presets, "Bedtime story preset not saved"
    assert loaded_presets["news_announcer"]["speed"] == 1.0, "News announcer speed incorrect"
    
    # Restore original path
    kokoro_tts.USER_PRESETS_FILE = original_path
    
    # Clean up test file
    if os.path.exists(temp_presets_file):
        os.remove(temp_presets_file)
    
    print("✓ Preset management works correctly")


def test_model_params_access():
    """Test access to model parameters"""
    print("Testing model parameters access...")
    
    # Test that we can access the version
    assert VERSION.startswith("2."), f"Invalid version: {VERSION}"
    
    # Test emotion profiles structure
    emotions = get_all_emotion_profiles()
    for emotion, profile in emotions.items():
        assert isinstance(profile, dict), f"Profile for {emotion} is not a dict"
        assert "speed" in profile, f"Speed missing in {emotion} profile"
        assert "pitch" in profile, f"Pitch missing in {emotion} profile"
        assert "emphasis" in profile, f"Emphasis missing in {emotion} profile"
        assert isinstance(profile["speed"], (int, float)), f"Speed not numeric in {emotion}"
        assert isinstance(profile["pitch"], (int, float)), f"Pitch not numeric in {emotion}"
        assert isinstance(profile["emphasis"], str), f"Emphasis not string in {emotion}"
    
    # Test audio effects structure
    effects = get_all_audio_effects()
    for effect, params in effects.items():
        assert isinstance(params, dict), f"Params for {effect} is not a dict"
    
    print("✓ Model parameters access works correctly")


def test_advanced_features():
    """Test advanced features like speaker detection"""
    print("Testing advanced features...")
    
    # Test speaker detection with various formats
    test_dialogue = '''Alice: Hi Bob, how are you today?
Bob: I'm doing well, Alice. Thanks for asking!
Carol said: I'm glad to hear that both of you are doing well.
"Alice replied: "That's wonderful news!" - Reporter'''
    
    speakers = detect_speakers(test_dialogue)
    assert len(speakers) > 0, "No speakers detected"
    
    # Test assigning voices to speakers
    mock_voices = ["af_sarah", "am_adam", "bf_emma", "zf_xiaoxiao"]
    speaker_voices = assign_voices_to_speakers(speakers, mock_voices)
    
    # Check that each unique speaker has a voice assigned
    unique_speakers = list(set([s[0] for s in speakers]))
    for speaker in unique_speakers:
        assert speaker in speaker_voices, f"No voice assigned to speaker {speaker}"
        assert speaker_voices[speaker] in mock_voices, f"Assigned voice not in available voices"
    
    print("✓ Advanced features work correctly")


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print(f"Running comprehensive tests for Kokoro Desktop v{VERSION}")
    print("="*60)
    
    test_api_endpoints()
    test_preset_management()
    test_model_params_access()
    test_advanced_features()
    
    print("="*60)
    print("All comprehensive tests passed! ✓")


if __name__ == "__main__":
    run_comprehensive_tests()