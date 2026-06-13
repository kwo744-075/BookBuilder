# Available narration voices, shared by the app and the Voice Studio.
# Display name -> edge-tts voice id.
VOICE_MAP = {
    # Male
    "Eric": "en-US-EricNeural",
    "Andrew": "en-US-AndrewNeural",
    "Brian": "en-US-BrianNeural",
    "Christopher": "en-US-ChristopherNeural",
    "Ryan": "en-GB-RyanNeural",
    # Female (Sonia is British / European)
    "Aria": "en-US-AriaNeural",
    "Jenny": "en-US-JennyNeural",
    "Sonia": "en-GB-SoniaNeural",
}

# Default selection (matches the app's previous hardcoded voice).
DEFAULT_VOICE = "Eric"

# Narration speed options. Display label -> edge-tts --rate value.
SPEED_MAP = {
    "0.75x": "-25%",
    "0.9x": "-10%",
    "1.0x": "+0%",
    "1.1x": "+10%",
    "1.25x": "+25%",
    "1.5x": "+50%",
}

# Default speed (matches the app's previous hardcoded -10% rate).
DEFAULT_SPEED = "0.9x"
