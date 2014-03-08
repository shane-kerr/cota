import sys

import pprint

class dialog:
    def __init__(self, filename="dialog.txt"):
        self.messages = { }
        self.filename = filename
        # TODO: catch missing file and display reasonable message
        f = open(filename, "r")
        line_num = 0
        while True:
            (msg_id, msg_txt, line_num) = self._next_msg(f, line_num)
            if msg_id:
                self.messages[msg_id] = msg_txt
            else:
                break
    def _next_msg(self, f, line_num):
        # skip blank lines
        while True:
            s = f.readline()
            if s == '':
                return (None, None, None)
            line_num = line_num + 1
            if s.strip() != '':
                break
        # first non-blank line is the message identifer... can be anything
        msg_id = s.strip()
        # next line should be '----'
        s = f.readline()
        line_num = line_num + 1
        if s.strip() != '----':
            sys.stderr.write("Badly formatted dialog file \"%s\"; expecting starting '----' on line %d\n" % (self.filename, line_num))
            sys.exit(1)
        # now read everything up to the next '----' as the message
        msg_txt_paragraphs = []
        msg_txt_lines = []
        while True:
            s = f.readline()
            if s == '':
                sys.stderr.write("Badly formatted dialog file \"%s\"; no ending '----' for message \"%s\"\n" % (self.filename, msg_id))
                sys.exit(1)
            line_num = line_num + 1
            if s.strip() == '----':
                break
            # separate paragraphs by blank lines; we need to do this in 
            # order to handle word wrap and the like properly on 
            # variable-sized terminals
            if s.strip() == '':
                msg_txt_paragraphs.append(' '.join(msg_txt_lines))
                msg_txt_lines = []
            else:
                msg_txt_lines.append(s.strip())
        return (msg_id, '\n\n'.join(msg_txt_paragraphs), line_num)

if __name__ == "__main__":
    dia = dialog()
    pprint.pprint(dia.messages)
    
