Kokoro Desktop

    A CLI text-to-speech tool using the Kokoro model, supporting multiple languages, voices (with advanced multi-voice blending), and various input formats
     including EPUB books and PDF documents.

    Features

     - Multiple language and voice support
     - Advanced multi-voice blending with customizable weights (3+ voices)
     - EPUB, PDF and TXT file input support
     - Standard input (stdin) and | piping from other programs
     - Streaming audio playback
     - Split output into chapters
     - Adjustable speech speed
     - WAV and MP3 output formats
     - Chapter merging capability
     - Detailed debug output option
     - GPU Support

    Installation

     1 pip install kokoro-desktop

    Usage Examples

      1 # Basic usage
      2 kokoro-desktop input.txt output.wav --speed 1.2 --lang en-us --voice af_sarah
      3 
      4 # 2-way voice blend
      5 kokoro-desktop input.txt --voice "af_sarah:60,am_adam:40"
      6 
      7 # 3-way voice blend (NEW!)
      8 kokoro-desktop input.txt --voice "am_adam:40,af_sarah:35,bf_emma:25"
      9 
     10 # 4-way voice blend (NEW!)
     11 kokoro-desktop input.txt --voice "am_adam:30,af_sarah:25,bf_emma:25,zf_xiaoxiao:20"
     12 
     13 # Stream audio
     14 kokoro-desktop input.txt --stream
     15 
     16 # Process EPUB
     17 kokoro-desktop input.epub --split-output ./chunks/

    Multi-Voice Blending

    The NEW multi-voice blending allows combining 3 or more voices:
     - Format: "voice1:weight,voice2:weight,voice3:weight,..."
     - Supports unlimited voice combinations
     - Automatic weight normalization
     - Backwards compatible with 2-voice blends

    Supported Voices

    Over 50 voices across multiple languages including English (US/UK), French, Italian, Japanese, Chinese, and more.

    Prerequisites

     - Python 3.9-3.12

    Requires model files: kokoro-v1.0.onnx and voices-v1.0.bin
    Install 
     Method 1: Install from PyPI (Recommended)

     1 # Using uv (recommended)
     2 uv tool install kokoro-desktop
     3 
     4 # Using pip
     5 pip install kokoro-desktop

    Method 2: Install from Git

     1 # Using uv (recommended)
     2 uv tool install git+https://github.com/gondaliyashreyan1/Kokoro-Desktop
     3 
     4 # Using pip
     5 pip install git+https://github.com/gondaliyashreyan1/Kokoro-Desktop

    Method 3: Clone and Install Locally

      1 git clone https://github.com/gondaliyashreyan1/Kokoro-Desktop.git
      2 cd Kokoro-Desktop
      3 
      4 # With uv (recommended):
      5 uv venv
      6 uv pip install -e .
      7 
      8 # With pip:
      9 python -m venv .venv
     10 source .venv/bin/activate  # On Windows: .venv\Scripts\activate
     11 pip install -e .

    Method 4: Run Without Installation

      1 git clone https://github.com/gondaliyashreyan1/Kokoro-Desktop.git
      2 cd Kokoro-Desktop
      3 
      4 # With uv:
      5 uv venv
      6 uv sync
      7 
      8 # With pip:
      9 python -m venv .venv
     10 source .venv/bin/activate
     11 pip install -r requirements.txt

    Usage
    After installation, use the command as:

     1 kokoro-desktop --help
     After install, model files required to be in the same dir for auto detection 
     # Download voice data (bin format is preferred)
     # Download the model
        wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin
        wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx
