import textwrap

class history:
    def __init__(self, width, msg_id=1):
        self.width = width
        self.msgs = [ ]
        self.msg_id = msg_id
    def add(self, msg):
        self.msgs.append(("%d" % self.msg_id, msg))
        self.msg_id = self.msg_id + 1
    def set_width(self, width):
        self.width = width
    def __iter__(self):
        for n in range(len(self.msgs)-1, -1, -1):
            msg = self.msgs[n]
            msg_str = msg[0] + "-" + msg[1]
            lines = textwrap.wrap(msg_str, self.width, 
                                  subsequent_indent=(" " * (len(msg[0])+1)))
            lines.reverse()
            for line in lines:
                yield line
        raise StopIteration()

