; BEQ +31 e BNE -32 exatamente nos limites da codificacao.
ADDI R1, R0, 1
BEQ R0, R0, longe
retorno: JMP fim
.org 32
longe: ADDI R2, R0, 7
ADDI R3, R0, 9
BNE R1, R0, retorno
fim: JMP fim
