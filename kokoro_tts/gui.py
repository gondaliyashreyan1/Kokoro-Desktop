#!/usr/bin/env python3
"""
GUI interface for Kokoro Desktop
A graphical user interface for the text-to-speech application with multi-voice blending
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from kokoro_onnx import Kokoro
import numpy as np
import soundfile as sf
import sounddevice as sd

class KokoroDesktopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kokoro Desktop - Text-to-Speech")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize Kokoro model
        self.kokoro = None
        self.model_loaded = False
        
        # Variables
        self.model_path = tk.StringVar(value="./kokoro-v1.0.onnx")
        self.voices_path = tk.StringVar(value="./voices-v1.0.bin")
        self.speed_var = tk.DoubleVar(value=1.0)
        self.language_var = tk.StringVar(value="en-us")
        self.output_format_var = tk.StringVar(value="wav")
        self.voice_vars = []  # For voice blending
        self.voice_weights = []  # For voice blending weights
        
        self.setup_ui()
        self.load_model_if_exists()
        
    def setup_ui(self):
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text tab
        self.text_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Text Input")
        self.setup_text_tab()
        
        # File tab
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.file_frame, text="File Input")
        self.setup_file_tab()
        
        # Voice blending tab
        self.blend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.blend_frame, text="Voice Blending")
        self.setup_voice_blending_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_text_tab(self):
        # Text input
        text_label = ttk.Label(self.text_frame, text="Enter text to convert:")
        text_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.text_input = scrolledtext.ScrolledText(self.text_frame, height=10, width=70)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.text_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.convert_text_btn = ttk.Button(button_frame, text="Convert to Speech", command=self.convert_text)
        self.convert_text_btn.pack(side=tk.LEFT, padx=5)
        
        self.play_text_btn = ttk.Button(button_frame, text="Play Preview", command=self.play_text_preview)
        self.play_text_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_text_btn = ttk.Button(button_frame, text="Save to File", command=self.save_text_to_file)
        self.save_text_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_file_tab(self):
        # File input
        file_input_frame = ttk.LabelFrame(self.file_frame, text="File Input")
        file_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_input_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_file_var = tk.StringVar()
        ttk.Entry(file_input_frame, textvariable=self.input_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_input_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_input_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_file_var = tk.StringVar()
        ttk.Entry(file_input_frame, textvariable=self.output_file_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_input_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, padx=5, pady=5)
        
        # Control buttons
        file_button_frame = ttk.Frame(self.file_frame)
        file_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.convert_file_btn = ttk.Button(file_button_frame, text="Convert File", command=self.convert_file)
        self.convert_file_btn.pack(side=tk.LEFT, padx=5)
        
        self.play_file_btn = ttk.Button(file_button_frame, text="Play Preview", command=self.play_file_preview)
        self.play_file_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_voice_blending_tab(self):
        # Voice blending controls
        blend_control_frame = ttk.LabelFrame(self.blend_frame, text="Voice Blending Controls")
        blend_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Number of voices to blend
        ttk.Label(blend_control_frame, text="Number of voices to blend:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.num_voices_var = tk.IntVar(value=2)
        num_voices_spinbox = ttk.Spinbox(blend_control_frame, from_=1, to=10, textvariable=self.num_voices_var, width=5)
        num_voices_spinbox.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(blend_control_frame, text="Update Voices", command=self.update_voice_controls).grid(row=0, column=2, padx=5, pady=5)
        
        # Voice selection and weight controls
        self.voice_control_frame = ttk.LabelFrame(self.blend_frame, text="Voice Selection")
        self.voice_control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize with 2 voices
        self.update_voice_controls()
        
    def setup_settings_tab(self):
        # Model paths
        model_frame = ttk.LabelFrame(self.settings_frame, text="Model Paths")
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(model_frame, text="Model Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.model_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(model_frame, text="Browse", command=lambda: self.browse_file(self.model_path)).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(model_frame, text="Voices Path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.voices_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(model_frame, text="Browse", command=lambda: self.browse_file(self.voices_path)).grid(row=1, column=2, padx=5, pady=5)
        
        # Reload model button
        ttk.Button(model_frame, text="Reload Model", command=self.load_model_if_exists).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Other settings
        settings_frame = ttk.LabelFrame(self.settings_frame, text="General Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Speed control
        ttk.Label(settings_frame, text="Speed:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        speed_scale = ttk.Scale(settings_frame, from_=0.5, to=2.0, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        speed_value = ttk.Label(settings_frame, textvariable=self.speed_var)
        speed_value.grid(row=0, column=2, padx=5, pady=5)
        
        # Language selection
        ttk.Label(settings_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        lang_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, values=["en-us", "en-gb", "fr-fr", "it", "ja", "cmn"])
        lang_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Output format
        ttk.Label(settings_frame, text="Output Format:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.output_format_var, values=["wav", "mp3"])
        format_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[
                ("Text files", "*.txt"),
                ("EPUB files", "*.epub"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_file_var.set(filename)
            
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save output file",
            defaultextension=f".{self.output_format_var.get()}",
            filetypes=[
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_file_var.set(filename)
            
    def browse_file(self, var):
        filename = filedialog.askopenfilename()
        if filename:
            var.set(filename)
            
    def update_voice_controls(self):
        # Clear existing widgets
        for widget in self.voice_control_frame.winfo_children():
            widget.destroy()
            
        # Create new voice controls based on selected number
        num_voices = self.num_voices_var.get()
        
        # Initialize voice variables
        self.voice_vars = []
        self.voice_weights = []
        
        for i in range(num_voices):
            # Voice selection
            ttk.Label(self.voice_control_frame, text=f"Voice {i+1}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            
            voice_var = tk.StringVar()
            self.voice_vars.append(voice_var)
            
            # Get available voices if model is loaded
            available_voices = []
            if self.model_loaded and self.kokoro:
                try:
                    available_voices = list(self.kokoro.get_voices())
                except:
                    available_voices = ["af_sarah", "am_adam", "bf_emma", "zf_xiaoxiao"]  # fallback
            
            voice_combo = ttk.Combobox(self.voice_control_frame, textvariable=voice_var, values=available_voices, width=20)
            voice_combo.grid(row=i, column=1, padx=5, pady=5)
            if available_voices:
                voice_combo.set(available_voices[0] if available_voices else "")
            
            # Weight control
            ttk.Label(self.voice_control_frame, text="Weight %:").grid(row=i, column=2, sticky=tk.W, padx=5, pady=5)
            
            weight_var = tk.DoubleVar(value=100.0/num_voices if num_voices > 0 else 100.0)
            self.voice_weights.append(weight_var)
            
            weight_spinbox = ttk.Spinbox(self.voice_control_frame, from_=0, to=100, textvariable=weight_var, width=10)
            weight_spinbox.grid(row=i, column=3, padx=5, pady=5)
            
        # Add normalize weights button
        ttk.Button(self.voice_control_frame, text="Normalize Weights", command=self.normalize_weights).grid(row=num_voices, column=0, columnspan=4, pady=10)
        
    def normalize_weights(self):
        """Normalize all weights to sum to 100%"""
        total = sum(var.get() for var in self.voice_weights)
        if total == 0:
            return
            
        factor = 100.0 / total
        for var in self.voice_weights:
            var.set(var.get() * factor)
            
    def load_model_if_exists(self):
        """Load the model if files exist"""
        model_path = self.model_path.get()
        voices_path = self.voices_path.get()
        
        if os.path.exists(model_path) and os.path.exists(voices_path):
            try:
                self.kokoro = Kokoro(model_path, voices_path)
                self.model_loaded = True
                self.status_var.set("Model loaded successfully")
                
                # Update voice combo boxes if on voice blending tab
                if self.notebook.index(self.notebook.select()) == 2:  # Voice blending tab
                    self.update_voice_controls()
                    
            except Exception as e:
                self.model_loaded = False
                self.status_var.set(f"Failed to load model: {str(e)}")
        else:
            self.model_loaded = False
            self.status_var.set("Model files not found. Please check paths in Settings.")
            
    def convert_text(self):
        """Convert entered text to speech"""
        if not self.model_loaded:
            messagebox.showerror("Error", "Model not loaded. Please check settings.")
            return
            
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert.")
            return
            
        # Get selected voice or blend
        voice = self.get_selected_voice()
        
        # Run conversion in a thread to prevent UI freezing
        threading.Thread(target=self._convert_text_worker, args=(text, voice), daemon=True).start()
        
    def _convert_text_worker(self, text, voice):
        """Worker function for text conversion"""
        try:
            self.status_var.set("Converting text to speech...")
            
            samples, sample_rate = self.kokoro.create(
                text, 
                voice=voice, 
                speed=self.speed_var.get(), 
                lang=self.language_var.get()
            )
            
            # Play the audio
            sd.play(samples, sample_rate)
            sd.wait()
            
            self.status_var.set("Conversion completed successfully")
            
        except Exception as e:
            self.status_var.set(f"Error during conversion: {str(e)}")
            
    def play_text_preview(self):
        """Play a preview of the entered text"""
        self.convert_text()
        
    def save_text_to_file(self):
        """Save the converted text to a file"""
        if not self.model_loaded:
            messagebox.showerror("Error", "Model not loaded. Please check settings.")
            return
            
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert.")
            return
            
        # Get output file
        output_file = filedialog.asksaveasfilename(
            title="Save audio file",
            defaultextension=f".{self.output_format_var.get()}",
            filetypes=[
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ]
        )
        
        if not output_file:
            return
            
        # Get selected voice
        voice = self.get_selected_voice()
        
        # Run save in a thread
        threading.Thread(target=self._save_text_worker, args=(text, voice, output_file), daemon=True).start()
        
    def _save_text_worker(self, text, voice, output_file):
        """Worker function for saving text to file"""
        try:
            self.status_var.set("Converting and saving...")
            
            samples, sample_rate = self.kokoro.create(
                text, 
                voice=voice, 
                speed=self.speed_var.get(), 
                lang=self.language_var.get()
            )
            
            sf.write(output_file, samples, sample_rate)
            
            self.status_var.set(f"Saved to {output_file}")
            
        except Exception as e:
            self.status_var.set(f"Error saving file: {str(e)}")
            
    def convert_file(self):
        """Convert input file to speech"""
        if not self.model_loaded:
            messagebox.showerror("Error", "Model not loaded. Please check settings.")
            return
            
        input_file = self.input_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input file.")
            return
            
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file.")
            return
            
        # Run conversion in a thread
        threading.Thread(target=self._convert_file_worker, args=(input_file, output_file), daemon=True).start()
        
    def _convert_file_worker(self, input_file, output_file):
        """Worker function for file conversion"""
        try:
            self.status_var.set("Converting file...")
            
            # For now, just read the text file and convert
            # In a full implementation, this would handle EPUB/PDF processing
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
                
            voice = self.get_selected_voice()
            
            samples, sample_rate = self.kokoro.create(
                text, 
                voice=voice, 
                speed=self.speed_var.get(), 
                lang=self.language_var.get()
            )
            
            sf.write(output_file, samples, sample_rate)
            
            self.status_var.set(f"File converted and saved to {output_file}")
            
        except Exception as e:
            self.status_var.set(f"Error converting file: {str(e)}")
            
    def play_file_preview(self):
        """Play a preview of the input file"""
        if not self.model_loaded:
            messagebox.showerror("Error", "Model not loaded. Please check settings.")
            return
            
        input_file = self.input_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input file.")
            return
            
        # Run preview in a thread
        threading.Thread(target=self._play_file_preview_worker, args=(input_file,), daemon=True).start()
        
    def _play_file_preview_worker(self, input_file):
        """Worker function for playing file preview"""
        try:
            self.status_var.set("Preparing preview...")
            
            # Read the text file
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
                
            voice = self.get_selected_voice()
            
            samples, sample_rate = self.kokoro.create(
                text, 
                voice=voice, 
                speed=self.speed_var.get(), 
                lang=self.language_var.get()
            )
            
            sd.play(samples, sample_rate)
            sd.wait()
            
            self.status_var.set("Preview completed")
            
        except Exception as e:
            self.status_var.set(f"Error in preview: {str(e)}")
            
    def get_selected_voice(self):
        """Get the selected voice or voice blend"""
        if len(self.voice_vars) == 1:
            # Single voice
            return self.voice_vars[0].get()
        else:
            # Multi-voice blend
            voice_blend_parts = []
            for i, (voice_var, weight_var) in enumerate(zip(self.voice_vars, self.voice_weights)):
                voice_blend_parts.append(f"{voice_var.get()}:{weight_var.get():.1f}")
            return ",".join(voice_blend_parts)

def main():
    root = tk.Tk()
    app = KokoroDesktopGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()