#!/usr/bin/env python3
"""Assembler da ISA CPU16. Numeros Python (decimal, 0xhex); labels case-insensitive."""
from pathlib import Path
import argparse, re
OPS = {n:i for i,n in enumerate('ADD SUB AND OR SLT ADDI LD ST BEQ BNE JMP'.split())}
def assemble(source):
    labels, rows, pc = {}, [], 0
    for lineno, line in enumerate(source.splitlines(),1):
        line=line.split(';')[0].strip()
        if not line: continue
        if ':' in line:
            name,line=line.split(':',1); name=name.strip().upper()
            if not re.fullmatch(r'[A-Z_][A-Z_0-9]*',name) or name in labels:
                raise ValueError(f'Linha {lineno}: label invalido/duplicado')
            labels[name]=pc; line=line.strip()
            if not line: continue
        tokens=line.replace(',',' ').split(); op=tokens[0].upper()
        if op=='.ORG':
            if len(tokens)!=2: raise ValueError('.org exige um endereco')
            pc=int(tokens[1],0)
            if not 0<=pc<4096: raise ValueError('.org fora da memoria')
            continue
        if not 0<=pc<4096: raise ValueError('Programa excede memoria')
        rows.append((pc,lineno,op,tokens[1:],line)); pc+=1
    image=[0xF000]*4096; used=set(); listing=[]
    def number(s): return labels[s.upper()] if s.upper() in labels else int(s,0)
    def reg(s):
        if not re.fullmatch(r'[Rr][0-7]',s): raise ValueError(f'Registrador invalido: {s}')
        return int(s[1])
    for pc,lineno,op,args,line in rows:
        try:
            if pc in used: raise ValueError('Endereco sobreposto')
            used.add(pc)
            if op=='.WORD':
                if len(args)!=1: raise ValueError('.word exige um valor')
                w=number(args[0])
                if not -32768<=w<=65535: raise ValueError('.word fora de 16 bits')
                w &= 65535
            else:
                code=OPS[op]
                if len(args)!=(1 if op=='JMP' else 3): raise ValueError('Quantidade de operandos')
                w=code<<12
                if code<=4: w|=reg(args[0])<<9|reg(args[1])<<6|reg(args[2])<<3
                elif code<=9:
                    imm=number(args[2])
                    if code in (8,9) and args[2].upper() in labels: imm-=pc
                    if not -32<=imm<=31: raise ValueError('Imediato fora de -32..31')
                    w|=reg(args[0])<<9|reg(args[1])<<6|(imm&63)
                else:
                    target=number(args[0])
                    if not 0<=target<4096: raise ValueError('JMP fora de 0..4095')
                    w|=target
            image[pc]=w; listing.append(f'{pc:03X}  {w:04X}  {line}')
        except (KeyError,ValueError) as e: raise ValueError(f'Linha {lineno}: {e}') from e
    return image,listing

def write_image(path):
    image,listing=assemble(path.read_text())
    path.with_suffix('.hex').write_text(''.join(f'{w:04X}\n' for w in image))
    path.with_suffix('.mif').write_text('WIDTH=16;\nDEPTH=4096;\nADDRESS_RADIX=HEX;\nDATA_RADIX=HEX;\nCONTENT BEGIN\n'+''.join(f'  {i:03X} : {w:04X};\n' for i,w in enumerate(image))+'END;\n')
    path.with_suffix('.lst').write_text('\n'.join(listing)+'\n')
    return image
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('source',type=Path)
    write_image(p.parse_args().source)
