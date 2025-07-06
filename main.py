import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import threading
import keyboard
import json
import os
from datetime import datetime
import pyaudio
import wave
import tempfile

class VoiceMemoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Memo Transcriber")
        self.root.geometry("800x600")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # State variables
        self.is_recording = False
        self.notes = []
        self.notes_file = "voice_notes.json"
        self.settings_file = "voice_memo_settings.json"
        self.current_hotkey = "f9"  # Default hotkey
        
        # Load existing notes and settings
        self.load_notes()
        self.load_settings()
        
        # Setup GUI
        self.setup_gui()
        
        # Setup global hotkey (F9 by default)
        self.setup_hotkey()
        
        # Adjust microphone for ambient noise
        self.calibrate_microphone()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Voice Memo Transcriber", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control buttons
        self.record_button = ttk.Button(main_frame, text="Start Recording", 
                                       command=self.toggle_recording)
        self.record_button.grid(row=1, column=0, padx=(0, 10), pady=(0, 10))
        
        self.status_label = ttk.Label(main_frame, text=f"Press {self.current_hotkey.upper()} to start recording")
        self.status_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        clear_button = ttk.Button(main_frame, text="Clear All Notes", 
                                 command=self.clear_notes)
        clear_button.grid(row=1, column=2, pady=(0, 10))
        
        # Hotkey configuration
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)
        
        ttk.Label(hotkey_frame, text="Hotkey:").pack(side=tk.LEFT)
        
        self.hotkey_var = tk.StringVar(value=self.current_hotkey)
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=10)
        self.hotkey_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        change_hotkey_button = ttk.Button(hotkey_frame, text="Set Hotkey", 
                                         command=self.change_hotkey)
        change_hotkey_button.pack(side=tk.LEFT)
        
        ttk.Label(hotkey_frame, text="(e.g., f9, ctrl+shift+r, space)").pack(side=tk.LEFT, padx=(10, 0))
        
        # Notes display
        notes_label = ttk.Label(main_frame, text="Notes:")
        notes_label.grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        
        self.notes_text = scrolledtext.ScrolledText(main_frame, height=20, width=80)
        self.notes_text.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                            pady=(20, 0))
        
        # Display existing notes
        self.display_notes()
    
    def setup_hotkey(self):
        # Register hotkey
        try:
            keyboard.add_hotkey(self.current_hotkey, self.hotkey_pressed)
            print(f"Global hotkey {self.current_hotkey.upper()} registered successfully")
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
    
    def hotkey_pressed(self):
        """Handle hotkey press by dispatching to main thread"""
        self.root.after(0, self.toggle_recording)
    
    def change_hotkey(self):
        new_hotkey = self.hotkey_var.get().strip().lower()
        
        if not new_hotkey:
            messagebox.showerror("Error", "Please enter a hotkey")
            return
        
        try:
            # Remove old hotkey
            keyboard.unhook_all()
            
            # Test new hotkey
            keyboard.add_hotkey(new_hotkey, self.hotkey_pressed)
            
            # Update current hotkey
            self.current_hotkey = new_hotkey
            self.status_label.config(text=f"Press {self.current_hotkey.upper()} to start recording")
            
            # Save settings
            self.save_settings()
            
            messagebox.showinfo("Success", f"Hotkey changed to: {new_hotkey.upper()}")
            print(f"Hotkey changed to: {new_hotkey.upper()}")
            
        except Exception as e:
            # Restore original hotkey if new one fails
            try:
                keyboard.add_hotkey(self.current_hotkey, self.hotkey_pressed)
            except:
                pass
            messagebox.showerror("Error", f"Invalid hotkey: {new_hotkey}\n\nError: {e}")
            self.hotkey_var.set(self.current_hotkey)
    
    def calibrate_microphone(self):
        # Calibrate microphone for ambient noise in a separate thread
        def calibrate():
            try:
                with self.microphone as source:
                    # Reduced calibration time and energy threshold for better sensitivity
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # Lower energy threshold to be more sensitive to quiet speech
                    self.recognizer.energy_threshold = 300
                    # Allow for longer pauses without stopping
                    self.recognizer.pause_threshold = 1.5
                print("Microphone calibrated for ambient noise")
            except Exception as e:
                print(f"Microphone calibration failed: {e}")
        
        threading.Thread(target=calibrate, daemon=True).start()
    
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text="Recording... Press {} to stop".format(self.current_hotkey.upper()))
        
        # Play start beep
        self.play_beep("start")
        
        # Start recording in separate thread
        recording_thread = threading.Thread(target=self.record_audio, daemon=True)
        recording_thread.start()
    
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Processing...")
        
        # Play stop beep
        self.play_beep("stop")
    
    def play_beep(self, beep_type):
        """Play system beep - can be customized later"""
        import winsound
        if beep_type == "start":
            # Higher pitch for start
            winsound.Beep(600, 200)
        elif beep_type == "stop":
            # Lower pitch for stop
            winsound.Beep(400, 300)
    
    def record_audio(self):
        try:
            with self.microphone as source:
                # Listen for audio with longer timeout and phrase time limit
                # This allows for longer pauses without stopping
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=60)
            
            # Transcribe audio
            self.transcribe_audio(audio)
            
        except sr.WaitTimeoutError:
            # On timeout, stop recording exactly like hitting the button
            self.root.after(0, self.stop_recording)
        except Exception as e:
            self.root.after(0, self.stop_recording)
            self.root.after(0, lambda: self.status_label.config(text=f"Recording error: {e}"))
    
    def transcribe_audio(self, audio):
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            
            # Add to notes
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = {
                "timestamp": timestamp,
                "text": text
            }
            self.notes.append(note)
            
            # Update GUI and save
            self.root.after(0, self.update_after_transcription)
            
        except sr.UnknownValueError:
            self.root.after(0, self.stop_recording)
            self.root.after(0, lambda: self.status_label.config(text="Could not understand audio"))
        except sr.RequestError as e:
            self.root.after(0, self.stop_recording)
            self.root.after(0, lambda: self.status_label.config(text=f"Speech recognition error: {e}"))
        finally:
            # Always stop recording after transcription attempt
            self.root.after(0, self.stop_recording)
    
    def update_after_transcription(self):
        self.display_notes()
        self.save_notes()
        self.status_label.config(text="Note added! Press {} to record again".format(self.current_hotkey.upper()))
    
    def display_notes(self):
        self.notes_text.delete(1.0, tk.END)
        for note in self.notes:
            self.notes_text.insert(tk.END, f"[{note['timestamp']}]\n{note['text']}\n\n")
        
        # Scroll to bottom
        self.notes_text.see(tk.END)
    
    def clear_notes(self):
        if messagebox.askyesno("Clear Notes", "Are you sure you want to clear all notes?"):
            self.notes = []
            self.display_notes()
            self.save_notes()
    
    def load_notes(self):
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r') as f:
                    self.notes = json.load(f)
        except Exception as e:
            print(f"Error loading notes: {e}")
            self.notes = []
    
    def save_notes(self):
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(self.notes, f, indent=2)
        except Exception as e:
            print(f"Error saving notes: {e}")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_hotkey = settings.get('hotkey', 'f9')
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_hotkey = 'f9'
    
    def save_settings(self):
        try:
            settings = {
                'hotkey': self.current_hotkey
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup
            keyboard.unhook_all()

def main():
    app = VoiceMemoApp()
    app.run()

if __name__ == "__main__":
    main()