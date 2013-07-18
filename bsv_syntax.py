from HTMLParser import HTMLParser
import sys
import re

write = sys.stdout.write
#def write(x): pass

bsv_kw = re.compile(r'\b(method|module|interface|let|return|actionvalue|action|function|typeclass|type|instance)\b')
bsv_dt = re.compile(r'\b(int|UInt|ActionValue|Action|Put|Reg|FIFO|FIFOF)\b')
bsv_bn = re.compile(r'\b(\d+)\b')

def highlight_bsv(code):
    code = bsv_kw.sub(r'<span class="kw">\1</span>', code)
    code = bsv_dt.sub(r'<span class="dt">\1</span>', code)
    code = bsv_bn.sub(r'<span class="bn">\1</span>', code)
    return code
dbg = 0
class MyParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        ts = self.tag_stack
        if len(ts) > 0:
            if ts[-1][0] != 'head': ts.append((tag, attrs))
        else:
            ts.append((tag, attrs))

        if dbg: print ts
        write(self.get_starttag_text())

    def handle_endtag(self, tag):
        ts = self.tag_stack
        if len(ts) > 0 and ts[-1][0] != 'head':
            assert(ts.pop()[0] == tag)
        elif tag == 'head':
            ts.pop()

        if dbg: print ts
        write("</" + tag + ">")

    def handle_startendtag(self, tag, attrs):
        write(self.get_starttag_text())

    def handle_data(self, data):
        if self.is_bsv_code():
            write(highlight_bsv(data))
        else:
            write(data)

    def handle_charref(self, name):
        write("&" + name + ";")

    def handle_entityref(self, name):
        write("&" + name + ";")

    def handle_decl(self, name):
        write("<!" + name + ">")

    def handle_comment(self, data):
        write("<!--" + data + "-->")

    def handle_pi(self, data):
        write("<?" + data + ">")

    def is_bsv_code(self):
        ts = self.tag_stack
        return len(ts) > 1 and ts[-1][0] == 'code' and ts[-2][0] == 'pre' and ('class', 'bsv') in ts[-2][1]

myparse = MyParser();
myparse.feed(open(sys.argv[1]).read())