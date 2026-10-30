# Roteiro para entender e apresentar

## O caminho de uma instrução

1. PC seleciona a palavra na RAM. FETCH_REQ permite a leitura síncrona.
2. FETCH_LATCH captura RI e RDM, guarda IP e incrementa PC.
3. DECODE seleciona Rj e Rk (ou Ri em ST/BEQ/BNE) e salva A e B.
4. EXECUTE calcula na ULA, resolve saltos ou prepara acesso à memória.
5. WRITEBACK grava resultado em Ri; LD passa antes por espera e captura de dado.

## Perguntas prováveis

**Por que oito registradores?** Cada índice ocupa 3 bits: 2³ = 8.

**Por que o imediato precisa de extensão de sinal?** Repetir o bit 5 nas posições
superiores preserva os valores negativos. 111111 representa -1 e vira FFFF.

**Como funciona ST?** A recebe Rj, B recebe Ri. A ULA soma A com o imediato.
STORE_MEM usa os 12 bits inferiores de ALUOut como endereço e B como dado.
A escrita só é habilitada quando chega um pulso e reset está inativo.

**Como funciona LD?** A ULA calcula o endereço, LOAD_WAIT permite leitura síncrona,
LOAD_CAPTURE salva RDM e WRITEBACK copia RDM para Ri.

**Por que salvar IP?** O PC já foi incrementado na busca; o salto relativo do
projeto precisa do endereço original da instrução. Exemplo: em endereço 10,
um BEQ com -3 deve ir para 7, não para 8.

**Como o SLT trata negativos?** Compara signed(A) e signed(B), não apenas o sinal
da subtração. Isso evita erros quando a subtração transborda.

**O botão é o clock?** Ele controla o avanço, mas o clock elétrico é CLOCK_50.
Dois flip-flops sincronizam o botão, o contador filtra bounce e um pulso habilita
um estado da CPU. A RAM continua recebendo clock enquanto a CPU está pausada.

**O que aparece na ULA?** O último resultado capturado em EXECUTE. O registrador
ALUOut permite enxergar esse resultado enquanto o botão não é pressionado.

**Por que o PC muda antes da instrução acabar?** Incremento ocorre na captura da
instrução. Em JMP/BEQ/BNE tomados ele é sobrescrito no estado de execução.

**Como saber que terminou?** Não há HALT; o programa termina logicamente em
JMP para seu próprio endereço. Na simulação, o testbench encerra após verificar
uma execução desse JMP, não porque a CPU tem uma instrução especial de parada.

**O que foi validado?** Os logs mostram simulação RTL e o relatório diferencia
isso de síntese/fitter Quartus e teste físico, ainda pendentes nesta versão.

**Onde estão controle e banco?** Ambos em cpu_core.vhd: state é a FSM; regs é o
banco de oito registradores. A ULA combinacional fica em alu.vhd.

## Divisão sugerida de estudo (adaptar ao grupo)

- Integrante 1: ISA, formatos e assembler.
- Integrante 2: caminho de dados e ULA.
- Integrante 3: máquina de estados e memória.
- Integrante 4: FPGA, debouncer e displays.
- Integrante 5, se houver: testes, resultados e integração.

Todos devem conseguir explicar o fluxo completo; essa divisão não substitui
participação nas aulas nem autoria da validação que o grupo realizar.
