# Voice Memo Transcriber

A desktop application that uses global hotkeys to capture audio from your microphone and transcribe it to text using speech recognition. Features a dark mode UI for easy note management and voice command functionality.

## Features

- **Global Hotkey Recording**: Press F9 (configurable) to start/stop voice recording from anywhere
- **Real-time Transcription**: Converts speech to text using Google Speech Recognition
- **Dark Mode UI**: Clean, modern interface with dark theme
- **Voice Commands**: Execute system commands and custom actions via voice
- **Note Management**: Save, edit, and manage transcribed notes
- **Persistent Storage**: Automatically saves notes and settings to JSON files
- **Windows Executable**: Ready-to-use .exe file included

## System Requirements

- **Platform**: Windows Desktop
- **Python**: 3.7+ (for development)
- **Microphone**: Required for voice input
- **Internet**: Required for speech recognition service

## Quick Start

### Using the Pre-built Executable

1. Download `Voice Memo Transcriber.exe` from the `exe/` folder
2. Run the executable
3. Press F9 to start/stop recording
4. Your transcribed text will appear in the application window

### Usage

- **Start Recording**: Press F9 (or your configured hotkey)
- **Stop Recording**: Press F9 again
- **Change Hotkey**: Use the settings menu in the application
- **Save Notes**: Notes are automatically saved to `voice_notes.json`

## Installation for Development

### Prerequisites

```bash
pip install speechrecognition pyaudio keyboard tkinter
```

### Running from Source

1. Clone or download the repository
2. Navigate to the `code/` directory
3. Install dependencies:

   ```bash
   pip install -r requirements.txt  # if available
   # or install manually:
   pip install speechrecognition pyaudio keyboard
   ```

4. Run the application:

   ```bash
   python main.py
   ```