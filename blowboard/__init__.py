"""...Docstring
"""

__version__ = '0.0.1'

config = {
    # Audio config
    'audio_channels': 1,  # The number of samples per frame
    'sample_rate': 44100,  # The number of samples per second

    # PyAudio streaming config
    'frames_per_buffer': 1024,  # Number of frames read at a time
    'portaudio_device_index': 1,

    # FFT config
    'fft_chunk_size': 2048,
    'fft_hop_length': 512,

    # Blowboard config
    'parse_block_length_ms': 500,  # Number of ms between each check for key-out
    'prominence_threshold': 400000,
    'whistle_hz_lower': 500,
    'whistle_hz_upper': 4200,
}