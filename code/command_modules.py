# Command modules configuration
# This file defines all available voice command modules and their commands

COMMAND_MODULES = {
    "spotify": {
        "description": "Control Spotify music player",
        "commands": {
            "open": {
                "phrases": ["open spotify", "start spotify", "launch spotify"],
                "description": "Opens the Spotify application"
            },
            "close": {
                "phrases": ["close spotify", "quit spotify", "exit spotify"],
                "description": "Closes the Spotify application"
            },
            "play_pause": {
                "phrases": [
                    "play spotify", "pause spotify", "spotify play", "spotify pause",
                    "play song", "pause song", "start song", "stop song",
                    "play music", "pause music", "resume music"
                ],
                "description": "Toggles play/pause for current track"
            },
            "next": {
                "phrases": ["next song", "skip song", "spotify next", "next track"],
                "description": "Skips to the next track"
            },
            "previous": {
                "phrases": ["previous song", "last song", "spotify previous", "previous track"],
                "description": "Goes back to the previous track"
            },
            "like": {
                "phrases": ["like song", "love song", "spotify like", "heart song"],
                "description": "Likes/unlikes the current song"
            }
        }
    },
    "system": {
        "description": "Basic system commands",
        "commands": {
            "volume_up": {
                "phrases": ["volume up", "increase volume", "louder"],
                "description": "Increases system volume"
            },
            "volume_down": {
                "phrases": ["volume down", "decrease volume", "quieter"],
                "description": "Decreases system volume"
            },
            "mute": {
                "phrases": ["mute", "silence", "turn off sound"],
                "description": "Mutes/unmutes system audio"
            },
            "screenshot": {
                "phrases": ["take screenshot", "screenshot", "capture screen"],
                "description": "Takes a screenshot"
            }
        }
    },
    "browser": {
        "description": "Web browser control commands",
        "commands": {
            "open_browser": {
                "phrases": ["open browser", "open chrome", "start browser", "open brave browser", "launch browser"],
                "description": "Opens the default web browser"
            },
            "refresh": {
                "phrases": ["refresh", "reload page", "refresh page"],
                "description": "Refreshes the current page"
            }
        }
    },
    "window": {
        "description": "Window management commands",
        "commands": {
            "minimize": {
                "phrases": ["minimize window", "minimize"],
                "description": "Minimizes the current window"
            },
            "maximize": {
                "phrases": ["maximize window", "maximize"],
                "description": "Maximizes the current window"
            },
            "close_window": {
                "phrases": ["close window", "close this window"],
                "description": "Closes the current window"
            },
        }
    }
}