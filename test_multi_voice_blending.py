#!/usr/bin/env python3
"""
Test script to verify multi-voice blending functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from kokoro_tts import validate_voice, check_required_files

def test_multi_voice_parsing():
    """Test the parsing of multi-voice blend strings"""
    print("Testing multi-voice parsing functionality...")
    
    # Mock kokoro object for testing
    class MockKokoro:
        def get_voices(self):
            return [
                "af_sarah", "am_adam", "bf_emma", "zf_xiaoxiao", 
                "jm_kumo", "ff_siwis", "if_sara"
            ]
        
        def get_voice_style(self, voice):
            # Return a mock voice style (numpy array-like)
            import numpy as np
            # Create a unique array for each voice for testing purposes
            return np.ones(10) * hash(voice) % 100
    
    kokoro = MockKokoro()
    
    # Test cases
    test_cases = [
        # Single voice
        "af_sarah",
        # Two-way blend with weights
        "af_sarah:60,am_adam:40",
        # Two-way blend without weights (should default to 50-50)
        "af_sarah,am_adam",
        # Three-way blend with weights
        "af_sarah:40,am_adam:35,bf_emma:25",
        # Three-way blend without weights (should normalize to 33.33-33.33-33.33)
        "af_sarah,am_adam,bf_emma",
        # Four-way blend with weights
        "af_sarah:30,am_adam:25,bf_emma:25,zf_xiaoxiao:20",
        # Four-way blend without weights
        "af_sarah,am_adam,bf_emma,zf_xiaoxiao",
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case}")
        try:
            result = validate_voice(test_case, kokoro)
            if isinstance(result, (list, tuple)):
                print(f"  Result type: {type(result)}, length: {len(result)}")
            else:
                print(f"  Success: Got result of type {type(result)}")
            print("  ✓ Passed")
        except Exception as e:
            print(f"  ✗ Failed with error: {e}")
    
    print("\nMulti-voice parsing tests completed!")

if __name__ == "__main__":
    test_multi_voice_parsing()