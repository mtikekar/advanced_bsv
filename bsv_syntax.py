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

class MyParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append((tag, attrs))
        write(self.get_starttag_text())

    def handle_endtag(self, tag):
        assert(self.tag_stack.pop()[0] == tag)
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

    def is_bsv_code(self):
        ts = self.tag_stack
        return len(ts) > 1 and ts[-1][0] == 'code' and ts[-2][0] == 'pre' and ('class', 'bsv') in ts[-2][1]

myparse = MyParser();
myparse.feed(open(sys.argv[1]).read())
