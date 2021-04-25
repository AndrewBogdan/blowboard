"""Program entry point for Blowboard
"""

import logging
import warnings

from blowboard import __version__
from blowboard import listen


def main():
    """Program entry point.

    Prints the version number end exits.
    """

    print(f'Blowboard version {__version__}')

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    warnings.filterwarnings("ignore")

    listen.listen_pyaudio()


if __name__ == '__main__':

    main()
