# CPU16 - Laboratório de Arquitetura de Sistemas Computacionais

Projeto multiciclo em VHDL para **DE2-115**, com 11 instruções, RAM unificada de
4096 palavras de 16 bits, oito registradores, programas MIF, testbenches e relatório.

**Estado:** simulação GHDL executada; núcleo passou pela síntese genérica GHDL.
**Pendente:** compilar no Quartus, verificar timing/recursos e demonstrar na FPGA.
Não existe `.sof` produzido ou resultado físico medido neste pacote.

## Comece aqui

1. Leia `docs/especificacao.pdf` e as convenções abaixo.
2. Para a placa, abra `quartus/cpu16.qpf` no Quartus com suporte Cyclone IV E.
3. Para simulação no Linux, instale GHDL e Python 3 e execute:

```bash
bash tools/run_tests.sh
```

O script usa VHDL-2008, recria os programas, compara o RTL com o modelo Python
por instrução e grava `results/reference.log` e `results/ghdl.log`.
O modelo Python é uma especificação executável: não é a CPU que vai à FPGA.

## Organização

| Pasta | Conteúdo |
|---|---|
| `rtl/` | Núcleo, ULA, memória Quartus, botão, displays e top-level |
| `sim/` | Memória de simulação e quatro testbenches |
| `programs/` | Assembly, MIF, HEX simples, listagens, traces e resultados esperados |
| `quartus/` | Projeto da DE2-115, pinagem, SDC e programa selecionado |
| `tools/` | Assembler, modelo de referência, geração dos testes e relatório |
| `docs/` | Especificação PDF, fonte editável e roteiro de apresentação |
| `results/` | Logs reais da validação neste ambiente |

## Convenções da arquitetura

- R0 a R7: 16 bits, todos graváveis, todos zerados no reset. **R0 não é constante.**
- PC e IP internos: 12 bits; PC exibido com quatro dígitos, nibble superior zero.
- RAM unificada: 4096 x 16 bits; endereços de **palavras**, não bytes.
- ADD/SUB/ADDI: resultado módulo 65536; não há exceção nem flags de overflow.
- AND/OR: bit a bit. SLT: comparação com sinal em complemento de dois.
- Imediato: -32 a +31, extensão de sinal para 16 bits.
- LD/ST: endereço `(Rj + imediato) mod 4096`. Bits altos são descartados.
- BEQ/BNE: alvo `(IP + imediato) mod 4096`, onde IP é o endereço do desvio.
  O incremento antecipado do PC durante a busca não muda essa regra.
- JMP: endereço absoluto de 12 bits. Não existe delay slot.
- Opcodes B a F: estado FAULT, LEDG8 aceso, sem novas escritas até reset.
- Bits não usados do tipo R: assembler grava zero; hardware ignora.
- Não existe HALT no enunciado: `fim: JMP fim` mantém o programa em laço.
- Reset zera a CPU, **não restaura RAM**. Para recarregar o MIF, reprograme a FPGA.
- A RAM pode ser alterada por ST inclusive na área de código; não há proteção.

Essas escolhas resolvem ambiguidades do enunciado e devem ser apresentadas ao professor.

## Operação na DE2-115

- KEY0: reset, ativo em zero.
- KEY1: avança **um estado**, não uma instrução; solte entre apertos.
- HEX3..HEX0: PC em hexadecimal, HEX0 contém o dígito menos significativo.
- SW17=0: HEX7..HEX4 mostram RDM. SW17=1: mostram o resultado registrado da ULA.
- RDM recebe instruções em FETCH_LATCH e dados em LOAD_CAPTURE.
- CLOCK_50 é o clock real. O botão sincronizado produz clock-enable; não é usado
  como clock de lógica. Debounce padrão: 500000 ciclos, aproximadamente 10 ms.
- LEDG0..8: FETCH_REQ, FETCH_LATCH, DECODE, EXECUTE, LOAD_WAIT,
  LOAD_CAPTURE, WRITEBACK, STORE_MEM, FAULT, respectivamente.
- O LED indica o estado **atual**, cuja ação ocorre no próximo pulso.

## Compilar e gravar

1. Conferir que a placa é DE2-115 e o dispositivo é EP4CE115F29C7.
2. Conferir os jumpers: pinagem fornecida assume JP7=2,5 V e JP6=3,3 V.
   Se a configuração física diferir, ajustar os padrões de I/O correspondentes.
3. Abrir `quartus/cpu16.qpf`. O top-level é `fpga_top`.
4. Manter `rtl/memory_quartus.vhd` na síntese. **Não adicionar `sim/*.vhd`.**
   A arquitetura de RAM do simulador lê HEX simples; a do Quartus usa MIF via altsyncram.
5. Compilar (Processing > Start Compilation). Inspecionar erros, warnings,
   recursos, RAM inicializada e o Timing Analyzer para CLOCK_50 de 20 ns.
6. No Programmer, selecionar USB-Blaster e JTAG, adicionar o `.sof` gerado em
   `quartus/output_files/`, marcar Program/Configure e iniciar.
7. Pressionar KEY0 e seguir o roteiro abaixo. A programação JTAG é volátil.

A SDC exclui entradas humanas assíncronas e saídas visuais de requisitos de
interface síncrona. Não exclui os caminhos internos entre registradores.
Não declarar timing aprovado antes de conferir os relatórios do Quartus.

### Primeiro teste manual

O programa selecionado é `01_isa.mif`. Após reset, PC=0000, RDM=0000,
ULA=0000 e LEDG0 aceso. Em cinco apertos completos de KEY1:

| Aperto | Estado após aperto | PC | RDM | ULA registrada |
|---|---|---|---|---|
| 1 | FETCH_LATCH / LEDG1 | 0000 | 0000 | 0000 |
| 2 | DECODE / LEDG2 | 0001 | 520A | 0000 |
| 3 | EXECUTE / LEDG3 | 0001 | 520A | 0000 |
| 4 | WRITEBACK / LEDG6 | 0001 | 520A | 000A |
| 5 | FETCH_REQ / LEDG0 | 0001 | 520A | 000A |

A primeira instrução é `ADDI R1,R0,10`. Alterne SW17 para conferir 520A e 000A.
O laço final fica no endereço 000E: o PC alterna entre 000E e 000F conforme a fase.
Não confunda essa alternância com erro de salto.

### Trocar ou criar programa

```bash
python3 tools/assemble.py programs/meu_programa.asm
cp programs/meu_programa.mif quartus/program.mif
```

Recompile e regrave para atualizar a inicialização. No Windows, copie o arquivo
pelo Explorer. Labels em BEQ/BNE são traduzidos em deslocamentos relativos à própria
instrução. Números em BEQ/BNE já são deslocamentos. O assembler rejeita imediato
fora da faixa, registrador inválido, sobreposição de endereços e palavra fora de 16 bits.
`.org` escolhe o próximo endereço e `.word` grava um valor de 16 bits.
Posições não preenchidas recebem F000 (opcode inválido), para detectar execução acidental.
O `.hex` aqui é texto com uma palavra por linha, **não Intel HEX**; não use no lugar
do `.mif` do Quartus.

## Antes de entregar no Canvas

- Preencher os nomes dos 4 a 5 integrantes e a identificação do grupo no relatório.
- Fazer a compilação Quartus, registrar recursos/timing, testar a placa e incluir
  fotos/observações reais na seção de resultados físicos.
- Revisar as convenções com o professor e estudar o roteiro de apresentação.
- Declarar o uso de IA; não apresentar os arquivos gerados como trabalho sem assistência.
- Enviar PDF, fontes VHDL e programas MIF conforme o enunciado. O ZIP agrega também
  ferramentas auxiliares para reproduzir o trabalho.
