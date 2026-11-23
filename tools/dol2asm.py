import struct, subprocess, sys, os
dol, out = sys.argv[1], sys.argv[2]
d = open(dol,'rb').read()
off = struct.unpack('>18I', d[0:0x48]); adr = struct.unpack('>18I', d[0x48:0x90]); sz = struct.unpack('>18I', d[0x90:0xD8])
with open(os.path.join(out,'sections.txt'),'w') as f:
    for i in range(18):
        if sz[i]: f.write(f"{'T' if i<7 else 'D'}{i} {adr[i]:08X} {sz[i]:08X} off={off[i]:X}\n")
for i in range(18):
    if not sz[i]: continue
    b = os.path.join(out, f's{i}.bin'); open(b,'wb').write(d[off[i]:off[i]+sz[i]])
    if i < 7:
        e = os.path.join(out, f's{i}.elf')
        subprocess.run(['llvm-objcopy','-I','binary','-O','elf32-powerpc','--rename-section','.data=.text,code,alloc,load,readonly',f'--change-section-address=.text=0x{adr[i]:X}',b,e],check=True)
