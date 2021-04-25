"""Listen to an audio stream and interpret what whistles it corresponds to.

"""

import logging

import librosa
import numpy as np
import pyaudio

from blowboard import classifier
from blowboard import config as cfg
from blowboard import util
from blowboard import mic

def listen_pyaudio(timeout=np.inf):
    # Start PortAudio interface
    audio = pyaudio.PyAudio()
    # Get the audio stream
    logging.info(f"Opening PyAudio stream on device index "
                 f"{cfg['portaudio_device_index']}")
    stream = mic.get_pyaudio_stream(audio)

    # Listen to the stream forever
    last_time = 0.0

    spectro_df = None
    try:
        while last_time < timeout:
            block_output = poll_one_block(
                stream=stream,
                time=cfg['parse_block_length_ms']
            )

            spectro_matrix = block_output['signal_freq_magn']

            spectro_df = util.add_spectro_matrix_to_df(
                current_spectro_df=spectro_df,
                spectro_matrix=spectro_matrix,
            )

            spectro_df, _, _ = classifier.classify_spectro_df(spectro_df)

    finally:
        # Close stream
        stream.stop_stream()
        stream.close()

        # Close PortAudio interface
        audio.terminate()


def poll_one_block(stream, time):
    """Records from the stream for an amount of time, rounded up.

    Inputs:
        stream: a file-like
        time: the integer time in milliseconds

    Returns:
        A dictionary with the following:
            bytes_frames: the bytes read, still sorted into buffers of size
                frames_per_buffer
            signal_freq_magn: an amplitude spectrogram matrix. Of shape
                (1 + fft_chunk_size/2 (frequencies),
                    ~samples/fft_hop_length - 3 (times))
                The axes are:
                - (column) time, samples/hop length columns.
                - (row) frequency, indexed by librosa.fft_frequencies
                - (value) power, the strength of that frequency (in watts?)
    """

    # Setup
    bytes_frames = []
    float_frames = []
    frames_read = 0
    frames_to_read = int(cfg['sample_rate'] * time / 1000)

    # Read all the frames from the stream
    logging.info('Listening...')
    while frames_read < frames_to_read:
        # Read into the buffer
        bytes_data = stream.read(cfg['frames_per_buffer'])
        frames_read += cfg['frames_per_buffer']

        # Convert buffer into np.float32
        float_data = np.frombuffer(
            buffer=bytes_data,
            dtype=np.int16,
        ).astype(np.float32)

        # Add to frames
        bytes_frames.append(bytes_data)
        float_frames.append(float_data)

    # Concatenate poll into one block, corresponding to the linear signal
    signal_linear = np.concatenate(float_frames)
    logging.info(f'Read {frames_read} frames.')

    # FFT
    #  Gets the signal in complex time-frequency domain
    #  np.abs(M[f, t]) gives the magnitude at that frequency
    #  np.angle(M[f, t]) gives the phase at that frequency
    complex_time_freq_matrix = librosa.stft(
        y=signal_linear,
        n_fft=cfg['fft_chunk_size'],
        hop_length=cfg['fft_hop_length'],
        center=False,  # center must be False when reading from librosa.stream
    )
    #  This is the magnitude of the signal at each frequency
    magn_time_freq_matrix = np.abs(complex_time_freq_matrix)
    # TODO: perhaps remove noise through knowledge of the phase?

    # Pack output
    output = {
        'signal_freq_magn': magn_time_freq_matrix,
        'signal_bytes_frames': bytes_frames,
    }

    return output
