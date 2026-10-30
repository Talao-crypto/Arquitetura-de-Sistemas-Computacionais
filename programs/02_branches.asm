ADDI R1, R0, 3
ADDI R2, R0, 0
loop: ADDI R2, R2, 1
ADDI R1, R1, -1
BNE R1, R0, loop
BEQ R1, R0, igual
ADDI R7, R0, -1
igual: BNE R1, R0, erro
BEQ R2, R0, erro
JMP fim
erro: ADDI R7, R0, -1
fim: JMP fim
