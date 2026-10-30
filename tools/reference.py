#!/usr/bin/env python3
"""Modelo sequencial independente dos estados VHDL; gera oracle por instrucao."""
from pathlib import Path
import json

def signed(x): return x-65536 if x&32768 else x

def execute(image,limit=3000):
    mem=image.copy(); r=[0]*8; pc=0; trace=[]; visited=set(); branches=set()
    for _ in range(limit):
        ip=pc; w=mem[pc]; code=w>>12; i=(w>>9)&7; j=(w>>6)&7; k=(w>>3)&7
        n=w&63; n=n-64 if n&32 else n
        pc=(pc+1)&4095; address=65535; data=0
        visited.add(code)
        if code==0: r[i]=(r[j]+r[k])&65535
        elif code==1: r[i]=(r[j]-r[k])&65535
        elif code==2: r[i]=r[j]&r[k]
        elif code==3: r[i]=r[j]|r[k]
        elif code==4: r[i]=int(signed(r[j])<signed(r[k]))
        elif code==5: r[i]=(r[j]+n)&65535
        elif code==6: r[i]=mem[(r[j]+n)&4095]
        elif code==7:
            address=(r[j]+n)&4095; data=r[i]; mem[address]=data
        elif code in (8,9):
            take=(r[i]==r[j]) if code==8 else (r[i]!=r[j]); branches.add((code,take))
            if take: pc=(ip+n)&4095
        elif code==10: pc=w&4095
        else: raise ValueError(f'Opcode invalido em {ip:03X}')
        trace.append([pc,*r,address,data])
        if code==10 and pc==ip: break
    else: raise RuntimeError('Limite de instrucoes excedido')
    return trace,mem,visited,branches

def save_trace(path,image):
    trace,mem,ops,branches=execute(image)
    path.with_suffix('.trace').write_text(''.join(' '.join(f'{v:04X}' for v in row)+'\n' for row in trace))
    path.with_suffix('.expected.json').write_text(json.dumps({'instructions':len(trace),'pc':trace[-1][0], 'registers':trace[-1][1:9], 'opcodes':sorted(ops),'branch_outcomes':sorted(branches),'writes':[[t[9],t[10]] for t in trace if t[9]!=65535]},indent=2)+'\n')
    return trace,mem,ops,branches
