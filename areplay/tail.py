import gevent

#https://www.snip2code.com/Snippet/506288/Gevent-based-Tail-F-generator


class GeventTail():
    def __init__(self, *args, **kwargs):
        self.file_name = kwargs.pop('file_name')
        try:
            self.fd = os.open(self.file_name, os.O_RDONLY | os.O_NONBLOCK)
            os.lseek(self.fd, 0, os.SEEK_END)
        except:
            self.fd = None
        self.hub = gevent.get_hub()
        self.watcher = self.hub.loop.stat(self.file_name)

    def readline(self):
        while self.fd:
            lines = os.read(self.fd, 4096).splitlines()
            if lines:
                for line in lines:
                    yield line
            else:
                self.hub.wait(self.watcher)
