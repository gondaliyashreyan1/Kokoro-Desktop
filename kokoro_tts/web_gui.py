#!/usr/bin/env python3
"""
Modern web-based GUI for Kokoro Desktop
A web interface for the text-to-speech application with multi-voice blending
"""

import os
import tempfile
import threading
from flask import Flask, render_template_string, request, jsonify, send_file
from kokoro_onnx import Kokoro
import numpy as np
import soundfile as sf
import io
import base64

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kokoro Desktop - Modern Web Interface</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: none;
        }
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        .btn-outline-primary {
            border-color: #667eea;
            color: #667eea;
        }
        .btn-outline-primary:hover {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .voice-selector {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .voice-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        .voice-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
        }
        .progress-container {
            margin-top: 20px;
        }
        .audio-player {
            width: 100%;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="header text-center py-4 mb-5">
            <h1 class="display-4 fw-bold text-white">Kokoro Desktop</h1>
            <p class="lead text-white">Modern Text-to-Speech with Multi-Voice Blending</p>
        </div>

        <div class="row justify-content-center">
            <div class="col-lg-10">
                <div class="card p-4">
                    <h3 class="mb-4">Text to Speech Converter</h3>

                    <!-- Text Input -->
                    <div class="mb-4">
                        <label for="textInput" class="form-label">Enter your text:</label>
                        <textarea class="form-control" id="textInput" rows="6" placeholder="Type or paste your text here..."></textarea>
                    </div>

                    <!-- Voice Selection -->
                    <div class="mb-4">
                        <label class="form-label">Voice Configuration:</label>

                        <!-- Single Voice vs Multi-Voice Toggle -->
                        <div class="mb-3">
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="voiceMode" id="singleVoice" value="single" checked>
                                <label class="form-check-label" for="singleVoice">Single Voice</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="voiceMode" id="multiVoice" value="multi">
                                <label class="form-check-label" for="multiVoice">Multi-Voice Blend</label>
                            </div>
                        </div>

                        <!-- Single Voice Selector -->
                        <div id="singleVoiceSection">
                            <select class="form-select" id="voiceSelect">
                                <option value="">Loading voices...</option>
                            </select>
                        </div>

                        <!-- Multi-Voice Section -->
                        <div id="multiVoiceSection" style="display: none;">
                            <div id="voiceBlendingControls">
                                <!-- Voice blending controls will be added dynamically -->
                            </div>
                            <button type="button" class="btn btn-sm btn-outline-secondary mt-2" onclick="addVoiceControl()">+ Add Voice</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary mt-2" onclick="normalizeWeights()">Normalize Weights</button>
                        </div>
                    </div>

                    <!-- Language and Speed -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <label for="languageSelect" class="form-label">Language:</label>
                            <select class="form-select" id="languageSelect">
                                <option value="en-us">English (US)</option>
                                <option value="en-gb">English (GB)</option>
                                <option value="fr-fr">French</option>
                                <option value="it">Italian</option>
                                <option value="ja">Japanese</option>
                                <option value="cmn">Chinese (Mandarin)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label for="speedSlider" class="form-label">Speed: <span id="speedValue">1.0</span>x</label>
                            <input type="range" class="form-range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="1.0">
                        </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                        <button type="button" class="btn btn-outline-primary flex-fill" id="previewBtn">
                            <i class="fas fa-play"></i> Preview
                        </button>
                        <button type="button" class="btn btn-primary flex-fill" id="convertBtn">
                            <i class="fas fa-bolt"></i> Convert & Download
                        </button>
                    </div>

                    <!-- Progress Bar -->
                    <div class="progress-container" style="display: none;" id="progressContainer">
                        <div class="progress">
                            <div class="progress-bar progress-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                        </div>
                        <p class="text-center mt-2" id="progressText">Processing...</p>
                    </div>

                    <!-- Audio Player -->
                    <div id="audioPlayerContainer" style="display: none;">
                        <label class="form-label">Audio Preview:</label>
                        <audio class="audio-player" id="audioPlayer" controls></audio>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    <script>
        // DOM Elements
        const voiceModeRadios = document.querySelectorAll('input[name="voiceMode"]');
        const singleVoiceSection = document.getElementById('singleVoiceSection');
        const multiVoiceSection = document.getElementById('multiVoiceSection');
        const voiceSelect = document.getElementById('voiceSelect');
        const languageSelect = document.getElementById('languageSelect');
        const speedSlider = document.getElementById('speedSlider');
        const speedValue = document.getElementById('speedValue');
        const textInput = document.getElementById('textInput');
        const previewBtn = document.getElementById('previewBtn');
        const convertBtn = document.getElementById('convertBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressText = document.getElementById('progressText');
        const audioPlayerContainer = document.getElementById('audioPlayerContainer');
        const audioPlayer = document.getElementById('audioPlayer');
        const voiceBlendingControls = document.getElementById('voiceBlendingControls');

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadVoices();
            setupEventListeners();
        });

        // Setup event listeners
        function setupEventListeners() {
            // Voice mode toggle
            voiceModeRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'single') {
                        singleVoiceSection.style.display = 'block';
                        multiVoiceSection.style.display = 'none';
                    } else {
                        singleVoiceSection.style.display = 'none';
                        multiVoiceSection.style.display = 'block';
                    }
                });
            });

            // Speed slider
            speedSlider.addEventListener('input', function() {
                speedValue.textContent = this.value;
            });

            // Button clicks
            previewBtn.addEventListener('click', handlePreview);
            convertBtn.addEventListener('click', handleConvert);
        }

        // Load available voices
        function loadVoices() {
            fetch('/api/voices')
                .then(response => response.json())
                .then(data => {
                    const voices = data.voices;
                    voiceSelect.innerHTML = '';

                    voices.forEach(voice => {
                        const option = document.createElement('option');
                        option.value = voice;
                        option.textContent = voice;
                        voiceSelect.appendChild(option);
                    });

                    // Add default option if no voices loaded
                    if (voices.length === 0) {
                        voiceSelect.innerHTML = '<option value="">No voices available</option>';
                    }
                })
                .catch(error => {
                    console.error('Error loading voices:', error);
                    voiceSelect.innerHTML = '<option value="">Error loading voices</option>';
                });
        }

        // Add voice control for multi-voice blending
        function addVoiceControl(index = null, voice = '', weight = null) {
            // Calculate default weight based on total number of voices after adding this one
            const totalVoicesAfterAdd = document.querySelectorAll('.voice-item').length + 1;
            const defaultWeight = weight !== null ? weight : Math.floor(100 / totalVoicesAfterAdd);

            const voiceIndex = index !== null ? index : document.querySelectorAll('.voice-item').length;
            const voiceItem = document.createElement('div');
            voiceItem.className = 'voice-item';
            voiceItem.id = `voice-${voiceIndex}`;

            voiceItem.innerHTML = `
                <div class="voice-controls">
                    <select class="form-select form-select-sm voice-select" data-index="${voiceIndex}">
                        <option value="">Select voice...</option>
                    </select>
                    <span>Weight:</span>
                    <input type="number" class="form-control form-control-sm weight-input" value="${defaultWeight}" min="0" max="100" style="width: 80px;" data-index="${voiceIndex}">
                    <span>%</span>
                    <button type="button" class="btn btn-sm btn-danger" onclick="removeVoiceControl(${voiceIndex})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            voiceBlendingControls.appendChild(voiceItem);

            // Populate voice options after a short delay to ensure voices are loaded
            setTimeout(() => {
                const voiceSelectElement = voiceItem.querySelector('.voice-select');
                if (voiceSelectElement) {
                    // Clear existing options except the first one
                    voiceSelectElement.innerHTML = '<option value="">Select voice...</option>';

                    // Get options from the main voice selector
                    const mainVoiceOptions = document.querySelectorAll('#voiceSelect option');
                    mainVoiceOptions.forEach(option => {
                        if (option.value) {
                            const newOption = document.createElement('option');
                            newOption.value = option.value;
                            newOption.textContent = option.textContent;
                            if (option.value === voice) {
                                newOption.selected = true;
                            }
                            voiceSelectElement.appendChild(newOption);
                        }
                    });
                }
            }, 100);
        }

        // Remove voice control
        function removeVoiceControl(index) {
            const element = document.getElementById(`voice-${index}`);
            if (element) {
                element.remove();
            }
        }

        // Normalize weights to sum to 100%
        function normalizeWeights() {
            const weightInputs = document.querySelectorAll('.weight-input');
            if (weightInputs.length === 0) return;

            // Distribute evenly and ensure they sum to 100%
            const equalWeight = 100 / weightInputs.length;
            const roundedWeight = Math.floor(equalWeight * 10) / 10; // Round down to 1 decimal

            // Apply the rounded weight to all but the last one
            for (let i = 0; i < weightInputs.length - 1; i++) {
                weightInputs[i].value = roundedWeight;
            }

            // Calculate the last weight to ensure sum is exactly 100
            const sumOfPrevious = roundedWeight * (weightInputs.length - 1);
            const lastWeight = 100 - sumOfPrevious;
            weightInputs[weightInputs.length - 1].value = Math.round(lastWeight * 10) / 10;
        }

        // Add speed control to the UI
        function setupSpeedControls() {
            const settingsDiv = document.querySelector('.row.mb-4');
            if (!settingsDiv) return;

            // Create speed control row
            const speedRow = document.createElement('div');
            speedRow.className = 'row mb-4';
            speedRow.id = 'speedRow';

            speedRow.innerHTML = `
                <div class="col-md-6">
                    <label for="speedMultiplier" class="form-label">Speed Multiplier: <span id="speedMultiplierValue">1.0</span>x</label>
                    <input type="range" class="form-range" id="speedMultiplier" min="0.5" max="2.0" step="0.1" value="1.0">
                </div>
                <div class="col-md-6">
                    <label for="effectSelect" class="form-label">Audio Effect:</label>
                    <select class="form-select" id="effectSelect">
                        <option value="none">No effect</option>
                        <option value="reverb_light">Light Reverb</option>
                        <option value="reverb_heavy">Heavy Reverb</option>
                        <option value="echo">Echo</option>
                        <option value="radio">Radio</option>
                        <option value="megaphone">Megaphone</option>
                        <option value="telephone">Telephone</option>
                    </select>
                </div>
            `;

            settingsDiv.parentNode.insertBefore(speedRow, settingsDiv.nextSibling);

            // Add event listener for speed multiplier
            const speedSlider = document.getElementById('speedMultiplier');
            const speedValue = document.getElementById('speedMultiplierValue');

            speedValue.textContent = speedSlider.value;

            speedSlider.addEventListener('input', function() {
                speedValue.textContent = this.value;
            });
        }

        // Get selected speed multiplier and effect
        function getSelectedSpeedEffect() {
            const speedMult = document.getElementById('speedMultiplier')?.value || '1.0';
            const effect = document.getElementById('effectSelect')?.value || 'none';
            return { speedMultiplier: parseFloat(speedMult), effect };
        }

        // Get selected voice (single or multi-blend)
        function getSelectedVoice() {
            const mode = document.querySelector('input[name="voiceMode"]:checked').value;

            if (mode === 'single') {
                return voiceSelect.value;
            } else {
                // Multi-voice blend
                const voiceControls = document.querySelectorAll('.voice-item');
                const blendParts = [];
                const weights = [];

                voiceControls.forEach(control => {
                    const voiceSelectEl = control.querySelector('.voice-select');
                    const weightInput = control.querySelector('.weight-input');

                    if (voiceSelectEl && voiceSelectEl.value) {
                        // Get the weight value, default if not specified
                        let weight = 0;
                        if (weightInput && weightInput.value !== '') {
                            weight = parseFloat(weightInput.value) || 0;
                        } else {
                            // Default weight based on number of voices
                            weight = 100 / voiceControls.length;
                        }

                        blendParts.push({voice: voiceSelectEl.value, weight: weight});
                        weights.push(weight);
                    }
                });

                // Normalize weights to sum to 100%
                const totalWeight = weights.reduce((sum, w) => sum + w, 0);
                if (totalWeight > 0) {
                    const normalizedBlendParts = blendParts.map(item =>
                        `${item.voice}:${((item.weight / totalWeight) * 100).toFixed(1)}`
                    );
                    return normalizedBlendParts.join(',');
                } else {
                    // Fallback if all weights are 0
                    const defaultWeight = (100 / blendParts.length).toFixed(1);
                    return blendParts.map(item => `${item.voice}:${defaultWeight}`).join(',');
                }
            }
        }

        // Show progress
        function showProgress(message = 'Processing...') {
            progressText.textContent = message;
            progressContainer.style.display = 'block';
            audioPlayerContainer.style.display = 'none';
        }

        // Hide progress
        function hideProgress() {
            progressContainer.style.display = 'none';
        }

        // Play audio
        function playAudio(audioData) {
            const binaryData = Uint8Array.from(atob(audioData), c => c.charCodeAt(0));
            const blob = new Blob([binaryData], { type: 'audio/wav' });
            const url = URL.createObjectURL(blob);

            audioPlayer.src = url;
            audioPlayerContainer.style.display = 'block';

            // Auto-play
            setTimeout(() => {
                audioPlayer.play().catch(e => console.log('Auto-play prevented:', e));
            }, 100);
        }

        // Handle preview
        function handlePreview() {
            const text = textInput.value.trim();
            if (!text) {
                alert('Please enter some text to convert.');
                return;
            }

            const voice = getSelectedVoice();
            if (!voice) {
                alert('Please select a voice.');
                return;
            }

            // Get speed multiplier and effect
            const { speedMultiplier, effect } = getSelectedSpeedEffect();
            // Calculate final speed by multiplying the base speed with multiplier
            const finalSpeed = parseFloat(speedSlider.value) * speedMultiplier;

            showProgress('Generating audio preview...');

            fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice: voice,
                    speed: finalSpeed,
                    language: languageSelect.value,
                    effect: effect || undefined
                })
            })
            .then(response => response.json())
            .then(data => {
                hideProgress();

                if (data.success) {
                    playAudio(data.audio_data);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                hideProgress();
                alert('Error: ' + error.message);
                console.error('Error:', error);
            });
        }

        // Handle convert and download
        function handleConvert() {
            const text = textInput.value.trim();
            if (!text) {
                alert('Please enter some text to convert.');
                return;
            }

            const voice = getSelectedVoice();
            if (!voice) {
                alert('Please select a voice.');
                return;
            }

            // Get speed multiplier and effect
            const { speedMultiplier, effect } = getSelectedSpeedEffect();
            // Calculate final speed by multiplying the base speed with multiplier
            const finalSpeed = parseFloat(speedSlider.value) * speedMultiplier;

            showProgress('Converting and preparing download...');

            fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice: voice,
                    speed: finalSpeed,
                    language: languageSelect.value,
                    effect: effect || undefined
                })
            })
            .then(response => response.json())
            .then(data => {
                hideProgress();

                if (data.success) {
                    // Create download link
                    const binaryData = Uint8Array.from(atob(data.audio_data), c => c.charCodeAt(0));
                    const blob = new Blob([binaryData], { type: data.format });
                    const url = URL.createObjectURL(blob);

                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'kokoro-audio.wav';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);

                    playAudio(data.audio_data);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                hideProgress();
                alert('Error: ' + error.message);
                console.error('Error:', error);
            });
        }

        // Initialize with one voice control for multi-voice mode
        window.onload = function() {
            // Wait for voices to load before adding controls
            setTimeout(function() {
                addVoiceControl(0, '', null);
                setupSpeedControls(); // Add speed and effect controls
            }, 1000);
        };
    </script>
</body>
</html>
'''

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

    return render_template_string(HTML_TEMPLATE)

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
            from kokoro_tts import validate_voice
            processed_voice = validate_voice(voice, kokoro)
        elif voice not in kokoro.get_voices():
            # Validate single voice
            from kokoro_tts import validate_voice
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

def main():
    """Main function to run the web GUI"""
    load_model()
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    main()