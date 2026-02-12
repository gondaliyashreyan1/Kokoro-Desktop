#!/usr/bin/env python3
"""
Kokoro Desktop Web Application
A full-featured web application for text-to-speech with multi-voice blending
"""

import os
import tempfile
import threading
from flask import Flask, render_template, request, jsonify, send_file
from kokoro_onnx import Kokoro
import numpy as np
import soundfile as sf
import io
import base64
import json
from kokoro_tts import validate_voice, get_all_emotion_profiles, get_all_audio_effects

app = Flask(__name__)

# Global variables for the Kokoro model
kokoro = None
model_loaded = False
available_voices = []
available_languages = []

def load_model():
    """Load the Kokoro model if files exist"""
    global kokoro, model_loaded, available_voices, available_languages
    
    model_path = "./kokoro-v1.0.onnx"
    voices_path = "./voices-v1.0.bin"
    
    if os.path.exists(model_path) and os.path.exists(voices_path):
        try:
            kokoro = Kokoro(model_path, voices_path)
            model_loaded = True
            
            # Get available voices and languages
            available_voices = sorted(list(kokoro.get_voices()))
            available_languages = sorted(list(kokoro.get_languages()))
            
            print(f"Model loaded successfully. Available voices: {len(available_voices)}, languages: {len(available_languages)}")
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            model_loaded = False
    else:
        print("Model files not found. Please check that kokoro-v1.0.onnx and voices-v1.0.bin are in the current directory.")

@app.route('/')
def index():
    if not model_loaded:
        load_model()
    
    return render_template('index.html', 
                          voices=available_voices, 
                          languages=available_languages,
                          model_loaded=model_loaded)

@app.route('/api/convert', methods=['POST'])
def convert_text():
    if not model_loaded:
        return jsonify({"error": "Model not loaded"}), 500
    
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'af_sarah')
    speed = float(data.get('speed', 1.0))
    language = data.get('language', 'en-us')
    effect = data.get('effect', 'none')  # New effect parameter
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Process the voice blend if it contains commas (indicating multiple voices)
        processed_voice = voice
        if ',' in voice:
            # Use validate_voice to process the voice blend
            processed_voice = validate_voice(voice, kokoro)
        elif voice not in kokoro.get_voices():
            # Validate single voice
            processed_voice = validate_voice(voice, kokoro)
        
        # Create audio using the processed voice
        samples, sample_rate = kokoro.create(text, voice=processed_voice, speed=speed, lang=language)
        
        # Note: Actual audio effects would be applied here if the kokoro library supported them
        # For now, we pass the parameters along but the actual effects depend on the underlying library
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            sf.write(tmp_file.name, samples, sample_rate)
            audio_path = tmp_file.name
        
        # Encode to base64 for transmission
        with open(audio_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temp file
        os.unlink(audio_path)
        
        return jsonify({
            "success": True,
            "audio_data": audio_data,
            "format": "audio/wav",
            "effect": effect
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voices')
def get_voices():
    if not model_loaded:
        load_model()
    return jsonify({"voices": available_voices})

@app.route('/api/languages')
def get_languages():
    if not model_loaded:
        load_model()
    return jsonify({"languages": available_languages})

@app.route('/api/emotions')
def get_emotions():
    emotions = get_all_emotion_profiles()
    return jsonify({"emotions": emotions})

@app.route('/api/effects')
def get_effects():
    effects = get_all_audio_effects()
    return jsonify({"effects": effects})

@app.route('/api/status')
def get_status():
    return jsonify({
        "model_loaded": model_loaded,
        "voices_count": len(available_voices) if available_voices else 0,
        "languages_count": len(available_languages) if available_languages else 0
    })

def main():
    """Main function to run the web application"""
    load_model()
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    main()