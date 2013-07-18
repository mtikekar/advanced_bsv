from HTMLParser import HTMLParser
import sys
import re

write = sys.stdout.write
#def write(x): pass

bsv_kw = re.compile(r'\b(begin|method|module|interface|rule|let|return|actionvalue|action|function|typeclass|type|instance)\b')
bsv_dt = re.compile(r'\b(int|UInt|Integer|Int|Bit|ActionValue|Action|Put|Reg|FIFO|FIFOF)\b')
bsv_bn = re.compile(r'\b(\d+)\b')

def highlight_string(code):
    code = bsv_kw.sub(r'<span class="kw">\1</span>', code)
    code = bsv_dt.sub(r'<span class="dt">\1</span>', code)
    code = bsv_bn.sub(r'<span class="bn">\1</span>', code)
    return code

dbg = 0

def uptill(str, substr):
    assert(substr in str)
    return str[:str.find(substr)]

def upfrom(str, substr):
    assert(substr in str)
    return str[str.find(substr)+len(substr):]

in_comment = False
def highlight_bsv(block):
    global in_comment
    highlighted_lines = []
    for code in block.splitlines(True):
        #Multiline comment
        if in_comment and not r'*/' in code:
            highlighted_lines.append(code)
            continue
        if in_comment:
            in_comment = False
            highlighted_lines.append(uptill(code, r'*/'))
            highlighted_lines.append(r'*/')
            highlighted_lines.extend(highlight_bsv(upfrom(code, r'*/')))
            continue
        if r'/*' in code:
            highlighted_lines.append(highlight_string(uptill(code, r'/*')))
            highlighted_lines.append(r'/*')
            in_comment = True
            highlighted_lines.extend(highlight_bsv(upfrom(code, r'/*')))
            continue
        if r'//' in code:
            highlighted_lines.append(highlight_string(uptill(code, r'//')))
            highlighted_lines.append(r'//')
            highlighted_lines.append(upfrom(code, r'//'))
            continue
        highlighted_lines.append(highlight_string(code))
    return ''.join(highlighted_lines)

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
