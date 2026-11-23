import re, sys, bisect
syms=[]
for l in open(sys.argv[1]):
    m=re.match(r'(\S+) = \.\w+:0x([0-9A-Fa-f]+); // type:function size:0x([0-9A-Fa-f]+)', l)
    if m: syms.append((int(m.group(2),16), int(m.group(3),16), m.group(1)))
syms.sort(); addrs=[s[0] for s in syms]
for a in sys.argv[2:]:
    x=int(a,16); i=bisect.bisect_right(addrs,x)-1
    if i>=0 and x < syms[i][0]+syms[i][1]: print(f"{a}  {syms[i][2]}+0x{x-syms[i][0]:X}")
    else: print(a, '?')
