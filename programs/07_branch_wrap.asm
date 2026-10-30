; Desvio relativo negativo no endereco 000 retorna a FFF.
BEQ R0, R0, -1
fim: JMP fim
.org 4095
JMP fim
