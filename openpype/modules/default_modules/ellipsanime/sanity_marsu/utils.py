import sys, io
import traceback

class Stream(io.BytesIO):

    def write(self, data):
        super(Stream, self).write(str(data))


def run_sanity_check(sc):
    stream = Stream()
    try:
        name = str(sc.name())
    except:
        name = sc.__name__
    try:
        r = sc.check(stream)
    except:
        traceback.print_exc()
        r = False
    print
    print name
    print '=' * len(name)
    print stream.getvalue()
    return r