
from typing import Optional

import wave

import librosa
import numpy as np
import pandas as pd
import pyaudio
import matplotlib.pyplot as plt

from blowboard import config as cfg


def add_spectro_matrix_to_df(current_spectro_df: Optional[pd.DataFrame],
                             spectro_matrix: np.ndarray) -> pd.DataFrame:
    """Adds a spectrogram matrix to the existing spectrogram DataFrame."""

    last_time = 0
    if current_spectro_df is not None:
        last_time = current_spectro_df.columns[-1]

    new_spectro_df = pd.DataFrame(
        data=spectro_matrix,
    )

    new_spectro_df.columns = librosa.frames_to_time(
        frames=new_spectro_df.columns,
        sr=cfg['sample_rate'],
        hop_length=cfg['fft_hop_length'],
        n_fft=cfg['fft_chunk_size']
    ) + last_time

    new_spectro_df.index = frequency_hz
    # Trim it to the range of whistling
    new_spectro_df_slice = new_spectro_df[cfg['whistle_hz_lower']:
                                          cfg['whistle_hz_upper']]

    # This will work fine if current_spectro_df is None.
    spectro_df = pd.concat([current_spectro_df, new_spectro_df_slice], axis=1)
    return spectro_df


def save_wav(filename, audio_frames, audio: pyaudio.PyAudio):
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(cfg['audio_channels'])
    waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    waveFile.setframerate(cfg['sample_rate'])
    waveFile.writeframes(b''.join(audio_frames))
    waveFile.close()

def plot_spectro_matrix(spectro, ax=None, fig=None, **kwargs):
    ax = ax or plt.gca()
    fig = fig or plt.gcf()

    # Convert to dB
    spectro_db = librosa.amplitude_to_db(
        S=spectro,
        ref=np.max,
    )

    # Get C5-C8 range mask
    frequency_mask = (500 < frequency_hz) & (frequency_hz < 4200)

    # Plot
    img = librosa.display.specshow(
        data=spectro_db[frequency_mask],
        sr=cfg['sample_rate'],
        hop_length=cfg['fft_hop_length'],
        x_axis='time',
        y_axis='log',
        y_coords=frequency_hz[frequency_mask],
        ax=ax,
        **kwargs)
    ax.set_title('Power spectrogram')
    fig.colorbar(img, ax=ax, format="%+2.0f dB")


def plot_energy(ax, pcen_full):
    # Now we'll plot the pcen curves
    times = librosa.times_like(pcen_full, sr=cfg['sample_rate'], hop_length=cfg['fft_hop_length'])
    ax.plot(times, pcen_full, linewidth=3, alpha=0.25, label='Full signal PCEN')
    #times = librosa.times_like(pcen_blocks, sr=sr, hop_length=cfg['fft_hop_length'])
    #ax.plot(times, pcen_blocks, linestyle=':', label='Block-wise PCEN')
    ax.legend()


def plot_all(spectro, energy):
    fig, ax = plt.subplots(nrows=2, sharex=True)
    plot_spectrograph(ax[0], spectro)
    plot_energy(ax[1], energy)


frequency_hz = librosa.fft_frequencies(
    sr=cfg['sample_rate'],
    n_fft=cfg['fft_chunk_size']
)