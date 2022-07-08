import sys

from src.read_config import read_config
from src.utils import stop_exec


def main(config_file, playstore_secret):
    try:
        config = read_config(config_file)

    except Exception as e:
        print(e.args)
        stop_exec()


if __name__ == '__main__':
    main(*sys.argv)
