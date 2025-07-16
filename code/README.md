# voice-memo-transcriber

Voice-Memo-Transcriber uses global hotkeys to capture audio from your mic and then transcribe it to text,
and saves it into a text file / displays it in a UI for you to copy from.

Included is the source code as well as the .exe for Windows Desktop


# After Edits
# Copy to Windows

To copy the `voice-note` folder from WSL to your Windows directory, use the following command in your WSL terminal:

```bash
cp -r ~/projects/active/daily_use/voice-note/code/* /mnt/c/Users/lucas/Desktop/WindowsBuildsFromWSL/voice-note/
```

This will recursively copy all files and subfolders to your Windows path.

# then in your windows terminal

# 1
cd C:\Users\lucas\Desktop\WindowsBuildsFromWSL/voice-note

# 2
python -m PyInstaller --onefile --windowed --name="Voice Memo Transcriber" --icon=myicon.ico main.py

# 3 (optional)
in wsl
git rm -r --cached exe/
in windows
copy /Y "C:\Users\lucas\Desktop\WindowsBuildsFromWSL\voice-note\exe\Voice Memo Transcriber.exe" "\\wsl.localhost\Ubuntu\home\lucas\projects\active\daily_use\voice-note\exe\"

