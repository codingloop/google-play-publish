import sys


def stop_exec(message: str = None):
    if message:
        print(message)

    sys.exit(5)
