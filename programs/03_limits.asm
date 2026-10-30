; Base 256: dados separados do programa.
ADDI R6, R0, 16
ADD R6, R6, R6
ADD R6, R6, R6
ADD R6, R6, R6
ADD R6, R6, R6
LD R1, R6, 0
LD R2, R6, 1
SLT R3, R1, R2
SLT R4, R2, R1
ADDI R2, R2, 1
SUB R5, R1, R2
ADDI R7, R0, -32
ADDI R7, R7, 31
ST R7, R6, -32
LD R5, R6, -32
ST R3, R6, 31
LD R4, R6, 31
fim: JMP fim
.org 0x100
.word 0x8000
.word 0x7fff
