import sys


def name():
    return 'Test Check'


def check(stream=sys.stdout):
    stream.write('running test check...\n')
    return True


def highlight():
    pass


def resolve(stream=sys.stdout):
    pass