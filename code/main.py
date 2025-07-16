import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
import threading
import keyboard
import json
import os
from datetime import datetime
import winsound
from voice_commands import VoiceCommandManager
from command_modules import COMMAND_MODULES

class VoiceMemoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Memo Transcriber")
        self.root.geometry("900x700")
        
        # Dark mode color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'surface': '#2d2d2d',
            'primary': '#0d7377',
            'primary_hover': '#14a085',
            'secondary': '#404040',
            'success': '#4caf50',
            'danger': '#f44336',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize command manager
        self.command_manager = VoiceCommandManager()
        
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
    
    def create_button(self, parent, text, command, bg_color, hover_color=None, **kwargs):
        """Create a custom button with proper dark theme"""
        if hover_color is None:
            hover_color = bg_color
        
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg='white', relief='flat',
                       borderwidth=0, highlightthickness=0,
                       font=('Segoe UI', 10, 'bold'),
                       cursor='hand2', **kwargs)
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
        
        return btn
    
    def create_notebook_tab(self, parent, text, bg_color, selected_color, command):
        """Create a custom tab button"""
        tab = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=self.colors['text'], relief='flat',
                       borderwidth=0, highlightthickness=0,
                       font=('Segoe UI', 11, 'bold'),
                       cursor='hand2', padx=20, pady=10)
        
        # Hover and selection effects
        def on_enter(e):
            if tab != self.current_tab:
                tab.config(bg=self.colors['border'])
        
        def on_leave(e):
            if tab != self.current_tab:
                tab.config(bg=bg_color)
        
        tab.bind("<Enter>", on_enter)
        tab.bind("<Leave>", on_leave)
        
        return tab
    
    def setup_gui(self):
        # Create tab bar
        self.tab_frame = tk.Frame(self.root, bg=self.colors['bg'], height=50)
        self.tab_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.tab_frame.pack_propagate(False)
        
        # Create tab buttons
        self.main_tab_btn = self.create_notebook_tab(self.tab_frame, "Voice Memo", 
                                                    self.colors['surface'], self.colors['primary'],
                                                    lambda: self.switch_tab("main"))
        self.main_tab_btn.pack(side="left")
        
        self.commands_tab_btn = self.create_notebook_tab(self.tab_frame, "Commands",
                                                        self.colors['surface'], self.colors['primary'],
                                                        lambda: self.switch_tab("commands"))
        self.commands_tab_btn.pack(side="left")
        
        # Create content frames
        self.content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Main tab content
        self.main_frame = tk.Frame(self.content_frame, bg=self.colors['surface'], relief='flat')
        
        # Commands tab content
        self.commands_frame = tk.Frame(self.content_frame, bg=self.colors['surface'], relief='flat')
        
        self.setup_main_tab()
        self.setup_commands_tab()
        
        # Set initial tab
        self.current_tab = None
        self.switch_tab("main")
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        # Hide all frames
        self.main_frame.pack_forget()
        self.commands_frame.pack_forget()
        
        # Reset all tab colors
        self.main_tab_btn.config(bg=self.colors['surface'])
        self.commands_tab_btn.config(bg=self.colors['surface'])
        
        # Show selected tab and highlight button
        if tab_name == "main":
            self.main_frame.pack(fill="both", expand=True)
            self.main_tab_btn.config(bg=self.colors['primary'])
            self.current_tab = self.main_tab_btn
        elif tab_name == "commands":
            self.commands_frame.pack(fill="both", expand=True)
            self.commands_tab_btn.config(bg=self.colors['primary'])
            self.current_tab = self.commands_tab_btn
    
    def setup_main_tab(self):
        # Configure main frame
        self.main_frame.configure(bg=self.colors['surface'])
        
        # Title
        title_label = tk.Label(self.main_frame, text="Voice Memo Transcriber", 
                              bg=self.colors['surface'], fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Control buttons frame
        control_frame = tk.Frame(self.main_frame, bg=self.colors['surface'])
        control_frame.pack(pady=(0, 20), padx=20, fill='x')
        
        # Record button
        self.record_button = self.create_button(control_frame, "🎤 Start Recording", 
                                               self.toggle_recording, self.colors['primary'],
                                               self.colors['primary_hover'], padx=20, pady=10)
        self.record_button.pack(side="left", padx=(0, 15))
        
        # Status label
        self.status_label = tk.Label(control_frame, text=f"Press {self.current_hotkey.upper()} to start recording",
                                    bg=self.colors['surface'], fg=self.colors['primary'],
                                    font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side="left", padx=(15, 0))
        
        # Clear button
        clear_button = self.create_button(control_frame, "🗑️ Clear All Notes", 
                                         self.clear_notes, self.colors['danger'],
                                         '#c82333', padx=20, pady=10)
        clear_button.pack(side="right")
        
        # Hotkey configuration frame
        hotkey_frame = tk.LabelFrame(self.main_frame, text="Hotkey Configuration", 
                                    bg=self.colors['surface'], fg=self.colors['text'],
                                    font=('Segoe UI', 11, 'bold'), bd=1, relief='solid')
        hotkey_frame.pack(pady=(0, 20), padx=20, fill='x')
        
        hotkey_inner_frame = tk.Frame(hotkey_frame, bg=self.colors['surface'])
        hotkey_inner_frame.pack(fill='x', padx=15, pady=15)
        
        tk.Label(hotkey_inner_frame, text="Hotkey:", bg=self.colors['surface'], 
                fg=self.colors['text'], font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        self.hotkey_var = tk.StringVar(value=self.current_hotkey)
        self.hotkey_entry = tk.Entry(hotkey_inner_frame, textvariable=self.hotkey_var, 
                                    width=12, bg=self.colors['surface'], fg=self.colors['text'],
                                    insertbackground=self.colors['text'], bd=1, relief='solid')
        self.hotkey_entry.pack(side=tk.LEFT, padx=(10, 10))
        
        change_hotkey_button = self.create_button(hotkey_inner_frame, "Set Hotkey", 
                                                 self.change_hotkey, self.colors['secondary'],
                                                 '#5a6268', padx=15, pady=8)
        change_hotkey_button.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(hotkey_inner_frame, text="(e.g., f9, ctrl+shift+r, space)", 
                bg=self.colors['surface'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        # Notes display frame
        notes_frame = tk.LabelFrame(self.main_frame, text="Notes", 
                                   bg=self.colors['surface'], fg=self.colors['text'],
                                   font=('Segoe UI', 11, 'bold'), bd=1, relief='solid')
        notes_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Notes text area
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=15, width=80,
                                                   bg=self.colors['surface'],
                                                   fg=self.colors['text'],
                                                   font=('Segoe UI', 10),
                                                   borderwidth=0,
                                                   relief='flat',
                                                   highlightthickness=0,
                                                   selectbackground=self.colors['primary'],
                                                   selectforeground='white',
                                                   insertbackground=self.colors['text'])
        self.notes_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Style the scrollbar
        self.notes_text.vbar.config(bg=self.colors['surface'], troughcolor=self.colors['bg'],
                                   highlightthickness=0, bd=0)
        
        # Display existing notes
        self.display_notes()
    
    def setup_commands_tab(self):
        # Configure commands frame
        self.commands_frame.configure(bg=self.colors['surface'])
        
        # Title
        title_label = tk.Label(self.commands_frame, text="Available Voice Commands", 
                              bg=self.colors['surface'], fg=self.colors['text'],
                              font=('Segoe UI', 20, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Create scrollable frame for commands
        canvas = tk.Canvas(self.commands_frame, bg=self.colors['surface'], 
                          highlightthickness=0, borderwidth=0)
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(self.commands_frame, orient="vertical", command=canvas.yview,
                                bg=self.colors['surface'], troughcolor=self.colors['bg'],
                                highlightthickness=0, bd=0, width=16)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Display command modules
        for module_name, module_info in COMMAND_MODULES.items():
            # Module frame
            module_frame = tk.LabelFrame(scrollable_frame, 
                                        text=f"📋 {module_name.title()} Commands", 
                                        bg=self.colors['surface'], fg=self.colors['text'],
                                        font=('Segoe UI', 11, 'bold'), bd=1, relief='solid')
            module_frame.pack(fill="x", padx=20, pady=10)
            
            # Module description
            if module_info.get("description"):
                desc_label = tk.Label(module_frame, text=module_info["description"], 
                                     bg=self.colors['surface'], fg=self.colors['text_secondary'],
                                     font=('Segoe UI', 9))
                desc_label.pack(anchor="w", pady=(10, 10), padx=20)
            
            # Commands
            for command_name, command_info in module_info["commands"].items():
                command_frame = tk.Frame(module_frame, bg=self.colors['surface'])
                command_frame.pack(fill="x", pady=5, padx=20)
                
                # Command name
                name_label = tk.Label(command_frame, 
                                     text=f"• {command_name.replace('_', ' ').title()}:", 
                                     bg=self.colors['surface'], fg=self.colors['text'],
                                     font=('Segoe UI', 12, 'bold'))
                name_label.pack(anchor="w", pady=(0, 2))
                
                # Command phrases
                phrases_text = ", ".join([f'"{phrase}"' for phrase in command_info["phrases"]])
                phrases_label = tk.Label(command_frame, text=f"   Say: {phrases_text}", 
                                        bg=self.colors['surface'], fg=self.colors['text'],
                                        font=('Segoe UI', 10))
                phrases_label.pack(anchor="w", pady=(0, 2))
                
                # Command description
                if command_info.get("description"):
                    desc_label = tk.Label(command_frame, text=f"   {command_info['description']}", 
                                         bg=self.colors['surface'], fg=self.colors['text_secondary'],
                                         font=('Segoe UI', 9))
                    desc_label.pack(anchor="w", pady=(0, 10))
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20), padx=(0, 20))
    
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
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.recognizer.energy_threshold = 300
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
        self.record_button.config(text="⏹️ Stop Recording")
        self.status_label.config(text="Recording... Press {} to stop".format(self.current_hotkey.upper()))
        
        # Play start beep
        self.play_beep("start")
        
        # Start recording in separate thread
        recording_thread = threading.Thread(target=self.record_audio, daemon=True)
        recording_thread.start()
    
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="🎤 Start Recording")
        self.status_label.config(text="Processing...")
        
        # Play stop beep
        self.play_beep("stop")
    
    def play_beep(self, beep_type):
        """Play system beep"""
        if beep_type == "start":
            winsound.Beep(600, 200)
        elif beep_type == "stop":
            winsound.Beep(400, 300)
    
    def record_audio(self):
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=60)
            
            # Transcribe audio
            self.transcribe_audio(audio)
            
        except sr.WaitTimeoutError:
            self.root.after(0, self.stop_recording)
        except Exception as e:
            error_msg = f"Recording error: {e}"
            self.root.after(0, self.stop_recording)
            self.root.after(0, lambda msg=error_msg: self.status_label.config(text=msg))
    
    def transcribe_audio(self, audio):
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            text_lower = text.lower().strip()
            
            # Try to execute command
            command_result = self.command_manager.execute_command(text_lower)
            
            # Create note entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if command_result["executed"]:
                status = "EXECUTED" if command_result["success"] else "FAILED"
                note = {
                    "timestamp": timestamp,
                    "text": f"[COMMAND {status}] {text}",
                }
                status_text = f"Command {'executed' if command_result['success'] else 'failed'}: {text}"
            else:
                # Regular note
                note = {
                    "timestamp": timestamp,
                    "text": text
                }
                status_text = "Note added! Press {} to record again".format(self.current_hotkey.upper())
            
            self.notes.append(note)
            
            # Update GUI
            self.root.after(0, lambda: self.update_after_transcription(status_text))
            
        except sr.UnknownValueError:
            self.root.after(0, self.stop_recording)
            self.root.after(0, lambda: self.status_label.config(text="Could not understand audio"))
        except sr.RequestError as e:
            error_msg = f"Speech recognition error: {e}"
            self.root.after(0, self.stop_recording)
            self.root.after(0, lambda msg=error_msg: self.status_label.config(text=msg))
        finally:
            self.root.after(0, self.stop_recording)
    
    def update_after_transcription(self, status_text):
        self.display_notes()
        self.save_notes()
        self.status_label.config(text=status_text)
    
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