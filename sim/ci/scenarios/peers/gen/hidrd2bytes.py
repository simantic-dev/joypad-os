# Compile the hidrd XML of the DualSense USB report descriptor (dogtopus gist 894da226d73afb3bdd195df41b3a26aa,
# https://gist.github.com/dogtopus/894da226d73afb3bdd195df41b3a26aa) to HID descriptor bytes. Prints a Python bytes literal.
import re, sys
x = re.sub(r'<!--.*?-->', '', open(sys.argv[1]).read(), flags=re.S)
toks = re.findall(r'<(/?)(\w+)[^>]*?(/?)>([^<]*)', x)
out = bytearray(); page = 1
def item(tag, v, signed=False):
    if v is None: out.append(tag); return
    n = 1 if (v < 256 if not signed else -128 <= v < 128) else 2 if v < 65536 else 4
    if signed and v >= 128 and n == 1: n = 2
    out.append(tag | {1: 1, 2: 2, 4: 3}[n]); out.extend(v.to_bytes(n, 'little'))
val = lambda s: int(s.strip(), 16) if re.search('[A-Fa-f]', s.strip()) and not s.strip().isdigit() else int(s.strip())
names = {'desktop': 1, 'button': 9}
desk = {'gamepad': 5, 'x': 0x30, 'y': 0x31, 'z': 0x32, 'rx': 0x33, 'ry': 0x34, 'rz': 0x35, 'hat_switch': 0x39}
flags = {'variable': 2}
i = 0; stack = []; pend = None
for close, tag, selfc, text in toks:
    t = text.strip()
    if close or tag in ('descriptor',): 
        if close and tag == 'COLLECTION': out.append(0xc0)
        if close and tag in ('input', 'output', 'feature'):
            item({'input': 0x80, 'output': 0x90, 'feature': 0xb0}[tag], pend); pend = None
        continue
    if tag == 'usage_page':
        page = names.get(t) or int(t, 16); item(0x04, page)
    elif tag == 'usage':
        item(0x08, desk[t[8:]] if t.startswith('desktop_') else int(t, 16))
    elif tag == 'COLLECTION': out += bytes([0xa1, 1])
    elif tag == 'report_id': item(0x84, int(t))
    elif tag == 'logical_minimum': item(0x14, int(t), True)
    elif tag == 'logical_maximum': item(0x24, int(t), True)
    elif tag == 'physical_minimum': item(0x34, int(t), True)
    elif tag == 'physical_maximum': item(0x44, int(t), True)
    elif tag == 'usage_minimum': item(0x18, int(t, 16))
    elif tag == 'usage_maximum': item(0x28, int(t, 16))
    elif tag == 'report_size': item(0x74, int(t))
    elif tag == 'report_count': item(0x94, int(t))
    elif tag == 'unit': pend_unit = True
    elif tag == 'degrees': out += bytes([0x65, 0x14])
    elif tag == 'none': out += bytes([0x65, 0])
    elif tag in ('input', 'output', 'feature'): pend = 0
    elif tag == 'variable': pend |= 2
    elif tag == 'null_state': pend |= 0x40
# 'unit none' resets the unit (65 00); inserted by hand below where hidrd had it
print(len(out)); print(out.hex())
