"""Module for interfacing with microphone through PortAudio."""

import logging

import pyaudio

import blowboard
cfg = blowboard.config

def _config_pyaudio_mic(audio: pyaudio.PyAudio):
    """Do one-time setup of PyAudio to work with the system mic."""
    print('----------------------record device list---------------------')
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print('Input Device id ', i, ' - ', audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    print('-------------------------------------------------------------')
    cfg['portaudio_device_index'] = int(input())
    print('recording via index '+str(cfg['portaudio_device_index']))

def get_pyaudio_stream(audio: pyaudio.PyAudio):
    """Get an audio stream from PyAudio"""

    logging.info('Getting PyAudio stream')

    if cfg['portaudio_device_index'] < 0:
        _config_pyaudio_mic(audio)

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=cfg['audio_channels'],
        rate=cfg['sample_rate'],
        input=True,
        input_device_index=cfg['portaudio_device_index'],
        frames_per_buffer=cfg['frames_per_buffer']
    )

    return stream