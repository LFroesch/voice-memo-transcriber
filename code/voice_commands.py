import subprocess
import time
import psutil
import keyboard
import os
from command_modules import COMMAND_MODULES

class VoiceCommandManager:
    def __init__(self):
        self.command_map = self._build_command_map()
    
    def _build_command_map(self):
        """Build a flat dictionary mapping phrases to their command handlers"""
        command_map = {}
        
        for module_name, module_info in COMMAND_MODULES.items():
            for command_name, command_info in module_info["commands"].items():
                handler_name = f"{module_name}_{command_name}"
                
                # Map each phrase to the handler
                for phrase in command_info["phrases"]:
                    command_map[phrase.lower()] = handler_name
        
        return command_map
    
    def execute_command(self, text):
        """Execute a voice command if it matches any known phrase"""
        text_lower = text.lower().strip()
        
        if text_lower in self.command_map:
            handler_name = self.command_map[text_lower]
            handler = getattr(self, handler_name, None)
            
            if handler:
                try:
                    success = handler()
                    return {"executed": True, "success": success}
                except Exception as e:
                    print(f"Error executing command {handler_name}: {e}")
                    return {"executed": True, "success": False}
        
        return {"executed": False, "success": False}
    
    # Spotify Commands
    def spotify_open(self):
        """Open Spotify application"""
        try:
            # Method 1: Try to open via Windows Start menu
            try:
                subprocess.run(["start", "spotify:"], shell=True, check=True)
                print("Opened Spotify via protocol")
                return True
            except:
                pass
            
            # Method 2: Try direct executable
            try:
                subprocess.run(["spotify"], check=True)
                print("Opened Spotify via executable")
                return True
            except:
                pass
            
            # Method 3: Try common installation paths
            common_paths = [
                os.path.expanduser("~\\AppData\\Roaming\\Spotify\\Spotify.exe"),
                "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe",
                "C:\\Program Files\\Spotify\\Spotify.exe",
                "C:\\Program Files (x86)\\Spotify\\Spotify.exe"
            ]
            
            for path in common_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    subprocess.run([expanded_path])
                    print(f"Opened Spotify from {expanded_path}")
                    return True
            
            print("Could not find Spotify installation")
            return False
            
        except Exception as e:
            print(f"Failed to open Spotify: {e}")
            return False
    
    def spotify_close(self):
        """Close Spotify application"""
        try:
            # Method 1: Use taskkill command (most reliable)
            try:
                result = subprocess.run(['taskkill', '/f', '/im', 'Spotify.exe'], 
                                    capture_output=True, text=True)
                if result.returncode == 0:
                    print("Spotify closed via taskkill")
                    return True
            except:
                pass
            
            # Method 2: Kill Spotify process using psutil
            spotify_found = False
            for proc in psutil.process_iter():
                try:
                    proc_name = proc.name().lower()
                    if 'spotify' in proc_name:
                        proc.terminate()
                        spotify_found = True
                        print(f"Terminated process: {proc.name()}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if spotify_found:
                print("Spotify closed via process termination")
                return True
            
            print("Spotify process not found")
            return False
            
        except Exception as e:
            print(f"Failed to close Spotify: {e}")
            return False
    
    def spotify_play_pause(self):
        """Toggle play/pause using media keys"""
        try:
            keyboard.send('play/pause media')
            print("Sent media play/pause command")
            return True
        except Exception as e:
            print(f"Failed to send play/pause command: {e}")
            return False
    
    def spotify_next(self):
        """Skip to next track using media keys"""
        try:
            keyboard.send('next track')
            print("Sent media next track command")
            return True
        except Exception as e:
            print(f"Failed to skip track: {e}")
            return False
    
    def spotify_previous(self):
        """Go to previous track using media keys"""
        try:
            keyboard.send('previous track')
            print("Sent media previous track command")
            return True
        except Exception as e:
            print(f"Failed to go to previous track: {e}")
            return False
    
    def spotify_like(self):
        """Like/unlike current song in Spotify"""
        try:
            subprocess.run(["start", "spotify:"], shell=True, check=True)
            time.sleep(0.3)  # Give it a moment to focus
            
            # Send Alt+Shift+B (Spotify's like/unlike shortcut)
            keyboard.send('alt+shift+b')
            print("Sent like/unlike song command to Spotify")
            return True
        except Exception as e:
            print(f"Failed to like/unlike song: {e}")
            return False
    
    # System Commands
    def system_volume_up(self):
        """Increase system volume"""
        try:
            keyboard.send('volume up')
            print("Increased system volume")
            return True
        except Exception as e:
            print(f"Failed to increase volume: {e}")
            return False
    
    def system_volume_down(self):
        """Decrease system volume"""
        try:
            keyboard.send('volume down')
            print("Decreased system volume")
            return True
        except Exception as e:
            print(f"Failed to decrease volume: {e}")
            return False
    
    def system_mute(self):
        """Mute/unmute system audio"""
        try:
            keyboard.send('volume mute')
            print("Toggled system mute")
            return True
        except Exception as e:
            print(f"Failed to toggle mute: {e}")
            return False
    
    def system_screenshot(self):
        """Take a screenshot"""
        try:
            keyboard.send('win+shift+s')  # Windows screenshot tool
            print("Opened screenshot tool")
            return True
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return False
    
    # Browser Commands
    def browser_open_browser(self):
        """Open Brave browser"""
        try:
            # Method 1: Try common Brave installation paths (most reliable)
            brave_paths = [
                "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                os.path.expanduser("~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
                "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            ]
            
            for path in brave_paths:
                if os.path.exists(path):
                    subprocess.run([path])
                    print(f"Opened Brave from {path}")
                    return True
            
            # Method 2: Try to open Brave via command
            try:
                subprocess.run(["start", "brave"], shell=True, check=True)
                print("Opened Brave browser via command")
                return True
            except:
                pass
            
            # Method 3: Try opening with default browser using a URL
            try:
                subprocess.run(["start", "http://"], shell=True, check=True)
                print("Opened default browser")
                return True
            except:
                pass
            
            # Method 4: Use webbrowser module as fallback
            import webbrowser
            webbrowser.open("http://")
            print("Opened browser via webbrowser module")
            return True
            
        except Exception as e:
            print(f"Failed to open browser: {e}")
            return False
    
    def browser_refresh(self):
        """Refresh current page"""
        try:
            keyboard.send('f5')
            print("Refreshed page")
            return True
        except Exception as e:
            print(f"Failed to refresh page: {e}")
            return False
    
    # Window Commands
    def window_minimize(self):
        """Minimize current window"""
        try:
            keyboard.send('win+down')
            print("Minimized window")
            return True
        except Exception as e:
            print(f"Failed to minimize window: {e}")
            return False
    
    def window_maximize(self):
        """Maximize current window"""
        try:
            keyboard.send('win+up')
            print("Maximized window")
            return True
        except Exception as e:
            print(f"Failed to maximize window: {e}")
            return False
    
    def window_close_window(self):
        """Close current window"""
        try:
            keyboard.send('alt+f4')
            print("Closed window")
            return True
        except Exception as e:
            print(f"Failed to close window: {e}")
            return False
    
