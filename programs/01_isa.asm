; Cobertura das 11 instrucoes e R0 gravavel; endereco -1 vira FFF.
ADDI R1, R0, 10
ADDI R2, R0, -3
ADD R3, R1, R2
SUB R4, R1, R2
AND R5, R1, R2
OR R6, R1, R2
SLT R7, R2, R1
ST R3, R0, -1
LD R5, R0, -1
BEQ R5, R3, igual
ADDI R7, R0, -1
igual: BNE R1, R2, distinto
ADDI R7, R0, -1
distinto: ADDI R0, R0, 1
fim: JMP fim
