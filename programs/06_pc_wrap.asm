; Incremento do PC em FFF retorna a 000.
BNE R1, R0, fim
JMP 4095
fim: JMP fim
.org 4095
ADDI R1, R1, 1
