#!/usr/bin/env python3
from pathlib import Path
import random
from assemble import assemble,write_image
from reference import save_trace
root=Path(__file__).resolve().parents[1]; p=root/'programs'
rng=random.Random(20261030)
lines=['; Programa deterministico: 200 operacoes, dados em 256..287.', 'ADDI R6, R0, 16', *['ADD R6, R6, R6']*4]
for _ in range(200):
    op=rng.choice(['ADD','SUB','AND','OR','SLT','ADDI','LD','ST'])
    i=rng.choice([1,2,3,4,5,7]); j=rng.randrange(8); k=rng.randrange(8)
    if op in ('LD','ST'): lines.append(f'{op} R{i}, R6, {rng.randrange(32)}')
    elif op=='ADDI': lines.append(f'{op} R{i}, R{j}, {rng.randrange(-32,32)}')
    else: lines.append(f'{op} R{i}, R{j}, R{k}')
lines+=['fim: JMP fim','.org 256']+[f'.word {rng.randrange(65536)}' for _ in range(32)]
(p/'05_random.asm').write_text('\n'.join(lines)+'\n')
expected={'06_pc_wrap':[0,1,0,0,0,0,0,0], '07_branch_wrap':[0,0,0,0,0,0,0,0], '01_isa':[1,10,65533,7,13,7,65535,1], '02_branches':[0,0,3,0,0,0,0,0], '03_limits':[0,32768,32768,1,1,65535,256,65535], '04_offsets':[0,1,7,9,0,0,0,0]}
ops=set(); branches=set(); total=0
for path in sorted(p.glob('*.asm')):
    trace,mem,o,b=save_trace(path,write_image(path)); ops|=o; branches|=b; total+=len(trace)
    if path.stem in expected: assert trace[-1][1:9]==expected[path.stem],path
    print(f'{path.stem}: {len(trace)} instrucoes; R={trace[-1][1:9]}')
assert ops==set(range(11))
assert branches=={(8,True),(8,False),(9,True),(9,False)}
# Guardas do assembler, incluindo codificacao conhecida.
assert assemble('ADD R1,R2,R3')[0][0]==0x0298
assert assemble('ADDI R1,R0,-1')[0][0]==0x523f
for bad in ['ADDI R1,R0,32','ADDI R1,R0,-33','ADD R8,R0,R0','JMP 4096','x: JMP x\nx: JMP x','.org 4096\n.word 0','.word 65536','.org 0\n.word 0\n.org 0\n.word 1']:
    try: assemble(bad)
    except ValueError: pass
    else: raise AssertionError(bad)
print(f'PASS: oracle, assembler; {total} instrucoes, 11 opcodes, 4 resultados de desvio')
