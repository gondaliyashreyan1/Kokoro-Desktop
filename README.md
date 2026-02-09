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
