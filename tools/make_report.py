#!/usr/bin/env python3
"""Gera PDF vetorial e especificacao Markdown editavel. Requer reportlab."""
from pathlib import Path
from xml.sax.saxutils import escape
import json, math, re
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT_DIR=Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("CPUFont",str(FONT_DIR/"Vera.ttf")))
pdfmetrics.registerFont(TTFont("CPUFont-Bold",str(FONT_DIR/"VeraBd.ttf")))
pdfmetrics.registerFontFamily("CPUFont",normal="CPUFont",bold="CPUFont-Bold",italic="CPUFont",boldItalic="CPUFont-Bold")
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect, String, PolyLine, Polygon
from reportlab.graphics import renderSVG
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs'
navy=colors.HexColor('#152B46'); teal=colors.HexColor('#087F8C'); pale=colors.HexColor('#EAF2F7'); grey=colors.HexColor('#506174')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCPU',fontName='CPUFont-Bold',fontSize=30,leading=34,textColor=navy,spaceAfter=16))
styles.add(ParagraphStyle(name='SectionCPU',fontName='CPUFont-Bold',fontSize=19,leading=23,textColor=navy,spaceAfter=14))
styles.add(ParagraphStyle(name='BodyCPU',fontName='CPUFont',fontSize=9.4,leading=13,spaceAfter=9,textColor=navy))
styles.add(ParagraphStyle(name='SmallCPU',fontName='CPUFont',fontSize=8.2,leading=11,textColor=navy,spaceAfter=5))
styles.add(ParagraphStyle(name='CellCPU',fontName='CPUFont',fontSize=8,leading=10.5,textColor=navy))
styles.add(ParagraphStyle(name='KickerCPU',fontName='CPUFont-Bold',fontSize=10,leading=14,textColor=teal,spaceAfter=15))
story=[]; md=[]
def p(text,small=False):
    story.append(Paragraph(text,styles['SmallCPU' if small else 'BodyCPU'])); md.append(re.sub('<[^>]+>','',text)+'\n')
def title(n,t):
    if story: story.append(PageBreak())
    story.append(Paragraph(f'CPU16 / {n:02d}',styles['KickerCPU']));story.append(Paragraph(t,styles['SectionCPU']));md.append('\n## '+t+'\n')
def table(headers,rows,widths):
    vals=[[Paragraph(escape(str(x)),styles['CellCPU']) for x in row] for row in [headers,*rows]]
    t=Table(vals,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('LINEBELOW',(0,0),(-1,0),1,teal),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8FA')])]))
    story.append(t);story.append(Spacer(1,12))
    md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('\n',' ') for x in r)+' |' for r in rows)+'\n')
def box(d,x,y,w,h,text):
    d.add(Rect(x,y,w,h,rx=5,ry=5,fillColor=pale,strokeColor=teal,strokeWidth=1))
    lines=text.split('\n')
    for i,line in enumerate(lines):d.add(String(x+w/2,y+h/2+(len(lines)-1)*5-i*10-3,line,fontName='CPUFont',fontSize=8,textAnchor='middle',fillColor=navy))
def arrow(d,pts,label=None,lx=None,ly=None):
    d.add(PolyLine([v for pt in pts for v in pt],strokeColor=grey,strokeWidth=1.1))
    a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);size=5
    tri=[b[0],b[1],b[0]-size*math.cos(ang-.5),b[1]-size*math.sin(ang-.5),b[0]-size*math.cos(ang+.5),b[1]-size*math.sin(ang+.5)]
    d.add(Polygon(tri,fillColor=grey,strokeColor=grey))
    if label:d.add(String(lx,ly,label,fontName='CPUFont',fontSize=7,fillColor=grey))
def datapath():
    d=Drawing(490,455)
    box(d,150,385,145,45,'Banco R0..R7 / 8 x 16\n2 leituras / 1 escrita')
    box(d,85,310,60,30,'A = Rj');box(d,235,310,65,30,'B = Rk/Ri');box(d,355,310,110,30,'Extensao 6 -> 16')
    box(d,250,240,80,30,'MUX B / imm');box(d,85,240,95,30,'ULA / 16 bits')
    box(d,85,165,95,30,'ALUOut / 16');box(d,310,150,100,30,'MUX endereco')
    box(d,420,210,65,30,'PC / 12');box(d,310,80,100,40,'RAM 4096 x 16')
    box(d,310,15,100,30,'RDM / 16');box(d,425,80,60,40,'RI / 16')
    box(d,85,15,110,30,'MUX writeback')
    arrow(d,[(175,385),(115,365),(115,340)],'Rj',120,360)
    arrow(d,[(265,385),(267,340)],'Rk ou Ri',275,359)
    arrow(d,[(115,310),(115,270)])
    arrow(d,[(267,310),(267,270)])
    arrow(d,[(410,310),(410,285),(310,285),(310,270)])
    arrow(d,[(250,255),(180,255)],'alu_b',204,261)
    arrow(d,[(132,240),(132,195)],'alu_y',139,213)
    arrow(d,[(180,180),(260,180),(260,165),(310,165)],'bits 11..0',200,187)
    arrow(d,[(452,210),(452,165),(410,165)])
    arrow(d,[(360,150),(360,120)],'addr / 12',365,133)
    arrow(d,[(300,325),(340,325),(340,200),(290,200),(290,100),(310,100)],'B / dado ST',236,110)
    arrow(d,[(360,80),(360,45)],'q / 16',365,61)
    arrow(d,[(410,90),(425,90)])
    arrow(d,[(310,30),(195,30)])
    arrow(d,[(132,165),(132,45)])
    arrow(d,[(85,30),(25,30),(25,410),(150,410)],'Ri / RegWrite',30,440)
    d.add(String(160,68,'LD seleciona RDM; demais selecionam ALUOut.',fontSize=7,fillColor=grey))
    return d

def fsm():
    d=Drawing(490,335)
    for y,t in [(290,'FETCH_REQ'),(240,'FETCH_LATCH'),(190,'DECODE'),(140,'EXECUTE')]:box(d,190,y,110,30,t)
    for y in (290,240,190):arrow(d,[(245,y),(245,y-20)])
    box(d,20,65,105,35,'WRITEBACK');box(d,185,65,115,35,'LOAD_WAIT');box(d,335,65,115,35,'STORE_MEM')
    box(d,185,5,115,35,'LOAD_CAPTURE');box(d,370,140,80,30,'FAULT')
    arrow(d,[(190,150),(72,150),(72,100)],'R / ADDI',83,156)
    arrow(d,[(245,140),(245,100)],'LD',252,119)
    arrow(d,[(300,150),(325,150),(392,100)],'ST',337,124)
    arrow(d,[(300,160),(370,160)],'B..F',319,167)
    arrow(d,[(245,65),(245,40)])
    arrow(d,[(185,20),(72,20),(72,65)])
    arrow(d,[(20,83),(5,83),(5,305),(190,305)])
    arrow(d,[(450,83),(475,83),(475,305),(300,305)])
    arrow(d,[(190,160),(155,160),(155,280),(190,300)],'BEQ/BNE/JMP',45,275)
    return d

title(1,'Especificação do projeto')
story.append(Paragraph('CPU de 16 bits<br/>multiciclo',styles['TitleCPU']))
p('<b>Laboratório de Arquitetura de Sistemas Computacionais</b><br/>Plataforma: Terasic DE2-115 | Linguagem: VHDL | Versão: 30/10/2026')
p('<b>Identificação do grupo:</b> preencher número, turma e nomes dos 4 a 5 integrantes antes da entrega. Este documento registra a implementação produzida com assistência de IA; a validação física ainda deve ser realizada pelo grupo.')
table(['Entrega técnica','Situação nesta versão'],[['ISA, caminho de dados e controle','Implementados em VHDL'],['Programas e assembler','7 programas; arquivos .asm, .mif, .hex e listagens'],['Simulação RTL','17 execuções de testbench aprovadas'],['Síntese genérica do núcleo','Executada com GHDL; não equivale ao fitter Quartus'],['Quartus e placa física','Projeto preparado; compilação e testes pendentes']],[185,305])
p('<b>Topologia.</b> Arquitetura de memória unificada: instruções e dados compartilham uma RAM síncrona de 4096 palavras. Um banco de oito registradores fornece operandos à ULA. Registradores internos preservam instrução, operandos e resultados entre estados. A unidade de controle é uma máquina de estados descrita em <b>cpu_core.vhd</b>. Não há pipeline, interrupções ou cache.')
p('<b>Execução.</b> A CPU usa CLOCK_50 continuamente. KEY1 gera um clock-enable filtrado; cada aperto avança um estado. Essa organização permite observar a execução nos LEDs sem distribuir o sinal mecânico como clock. O programa padrão começa com ADDI R1,R0,10.')
p('<b>Limite da evidência.</b> Os resultados deste documento são de simulação e de síntese genérica do núcleo. Não foram medidos frequência máxima, ocupação final ou comportamento elétrico na FPGA. Não há arquivo .sof validado nesta versão.')

title(2,'Registradores e conjunto de instruções')
table(['Registradores','Quantidade / bits','Endereço ou seleção'],[['R0 a R7','8 x 16','000, 001, 010, 011, 100, 101, 110, 111'],['PC e IP','2 x 12','Internos; PC exibido com extensão por zeros'],['RI, A, B, RDM, ALUOut','5 x 16','Internos, não endereçáveis pelo programa'],['Estado da UC','9 estados','Enumeração; código físico definido na síntese']],[130,110,250])
p('Todos os registradores R0..R7 são graváveis e zeram no reset. IP preserva o endereço da instrução atual. A recebe Rj; B recebe Rk no tipo R e Ri para ST/BEQ/BNE.',True)
table(['Formato','Campos / posições de bits'],[['R','opcode [15:12] | Ri [11:9] | Rj [8:6] | Rk [5:3] | 000 [2:0]'],['I','opcode [15:12] | Ri [11:9] | Rj [8:6] | imediato [5:0]'],['J','opcode [15:12] | endereço absoluto [11:0]']],[55,435])
table(['Opcode','Instrução','Efeito'],[['0','ADD Ri,Rj,Rk','Ri = (Rj + Rk) mod 65536'],['1','SUB Ri,Rj,Rk','Ri = (Rj - Rk) mod 65536'],['2','AND Ri,Rj,Rk','AND bit a bit'],['3','OR Ri,Rj,Rk','OR bit a bit'],['4','SLT Ri,Rj,Rk','Ri = 1 se signed(Rj) < signed(Rk), senão 0'],['5','ADDI Ri,Rj,imm','Ri = (Rj + sext(imm)) mod 65536'],['6','LD Ri,Rj,imm','Ri = RAM[(Rj + sext(imm)) mod 4096]'],['7','ST Ri,Rj,imm','RAM[(Rj + sext(imm)) mod 4096] = Ri'],['8','BEQ Ri,Rj,imm','Se iguais: PC = (IP + imm) mod 4096'],['9','BNE Ri,Rj,imm','Se diferentes: PC = (IP + imm) mod 4096'],['A','JMP end','PC = end'],['B a F','Reservados','Entram em FAULT até reset']],[55,125,310])
p('Opcodes em hexadecimal. Imediato com sinal: -32..+31. Exemplo: ADDI R1,R0,-1 = 523F. Bits não usados do tipo R são ignorados pelo hardware. Sem flags de overflow e sem delay slot.',True)

title(3,'Caminho de dados')
d=datapath();story.append(d);renderSVG.drawToFile(d,str(OUT/'caminho_dados.svg'));md.append('![Caminho de dados](caminho_dados.svg)\n')
p('<b>Seleção e escrita.</b> O mux de endereço escolhe PC durante a busca ou ALUOut[11:0] para LD/ST. O mux da entrada B da ULA escolhe o operando salvo ou o imediato estendido. O mux de writeback seleciona RDM para LD e ALUOut nas operações aritméticas e lógicas.')
p('<b>Controle não desenhado nos barramentos.</b> RI fornece opcode, índices e imediato. A UC habilita as capturas e a escrita em memória. Os campos do RI selecionam o banco, o extensor e a função da ULA. As linhas que se cruzam sem ponto de junção não representam conexão.')
p('<b>Atualização do PC.</b> Em FETCH_LATCH: IP recebe PC e PC recebe PC+1. Em EXECUTE: JMP seleciona RI[11:0]; BEQ/BNE tomados selecionam IP+imm. Somadores de endereço do PC são separados da ULA de dados. PC e endereços efetivos usam aritmética módulo 4096.')
p('<b>Observação.</b> PC alimenta HEX3..0. RDM e ALUOut alimentam um mux controlado por SW17 para HEX7..4. ALUOut é a saída registrada da ULA, mantida estável entre passos.')

title(4,'Unidade de controle: estados')
d=fsm();story.append(d);renderSVG.drawToFile(d,str(OUT/'estados.svg'));md.append('![Estados](estados.svg)\n')
p('Toda transição depende de <b>step=1</b> na borda de subida de CLOCK_50. Com step=0, CPU e estado permanecem estáveis. Reset tem prioridade e leva a FETCH_REQ de qualquer estado; FAULT permanece até reset. Essas condições globais foram omitidas das setas para manter a legibilidade.',True)
table(['Estado / LEDG','Ação no próximo pulso','Próximo estado'],[['FETCH_REQ / 0','Endereço PC disponível à RAM','FETCH_LATCH'],['FETCH_LATCH / 1','RI=RDM=q; IP=PC; PC=PC+1','DECODE'],['DECODE / 2','A=Rj; B=Rk ou Ri','EXECUTE'],['EXECUTE / 3','ALUOut=ULA; resolve tipo e salto','Conforme opcode'],['LOAD_WAIT / 4','Mantém endereço efetivo para leitura','LOAD_CAPTURE'],['LOAD_CAPTURE / 5','RDM=q','WRITEBACK'],['WRITEBACK / 6','Ri=RDM (LD) ou ALUOut','FETCH_REQ'],['STORE_MEM / 7','RAM[endereço efetivo]=B','FETCH_REQ'],['FAULT / 8','Bloqueia avanço e escrita','FAULT']],[112,244,134])
p('Ciclos habilitados por instrução: ADD/SUB/AND/OR/SLT/ADDI = 5; ST = 5; LD = 7; BEQ/BNE/JMP = 4. “Ciclo” aqui significa um avanço de estado; entre apertos podem transcorrer muitos ciclos físicos de 50 MHz.',True)

title(5,'Sinais, memória e temporização')
table(['Sinal / largura','Significado e condição'],[['clk / 1','Clock de 50 MHz distribuído à CPU, RAM e filtro do botão'],['reset / 1','Reset interno ativo alto; prioridade sobre step; não limpa a RAM'],['step / 1','Pulso de um ciclo após pressionar KEY1 de forma estável'],['mem_addr / 12','PC, exceto LOAD_WAIT/LOAD_CAPTURE/STORE_MEM: ALUOut[11:0]'],['mem_data / 16','B, contendo Ri para ST'],['mem_q / 16','Saída da RAM síncrona'],['mem_we / 1','STORE_MEM AND step AND NOT reset'],['op / 4 lógicos','Opcode de RI; seleciona operação e fluxo'],['ri, rj, rk / 3 lógicos','Seletores do banco extraídos de RI'],['alu_b / 16','sext6 para ADDI/LD/ST; B para outras instruções'],['alu_y / 16','Resultado combinacional antes da captura em ALUOut'],['leds / 9','Um LED aceso para o estado atual'],['regs_debug / 128','Saída para verificação; não conectada no top físico']],[125,365])
p('<b>Habilitações internas.</b> IRWrite, RDMWrite, RegWrite e PCWrite são condições implícitas no processo sequencial, não portas separadas: RI/IP em FETCH_LATCH; RDM em FETCH_LATCH ou LOAD_CAPTURE; banco em WRITEBACK; PC em FETCH_LATCH ou EXECUTE de salto tomado/JMP. A/B carregam em DECODE, ALUOut em EXECUTE. Todas são condicionadas a step.')
p('<b>Leitura síncrona.</b> A RAM recebe clock mesmo enquanto a CPU está pausada. Em execução contínua, FETCH_REQ e LOAD_WAIT garantem a latência de leitura antes da captura. ST só escreve na borda com mem_we=1, evitando repetição de escrita durante a pausa em STORE_MEM.')
p('<b>Inicialização.</b> A arquitetura Quartus usa altsyncram em SINGLE_PORT, saída sem registrador adicional e arquivo program.mif. A arquitetura de simulação reproduz leitura síncrona e lê uma imagem HEX simples gerada a partir do mesmo assembly. Ambas têm 4096 palavras de 16 bits. Endereços não usados são F000.')
p('<b>Reset e limites.</b> KEY0 solicita reset; a liberação é sincronizada. Reset zera registradores, PC, RI e estado, mas mantém dados já escritos na RAM. Para reinicializar o programa/dados, regravar a configuração. Como não existe proteção de memória, ST pode alterar código; os testes usam áreas de dados separadas.')

title(6,'Testes e critérios de aprovação')
p('Os programas são montados por assemble.py e executados por reference.py, um modelo sequencial independente da FSM. O testbench compara PC e os oito registradores após cada instrução, além do endereço e dado de cada ST. Valores finais dirigidos também são comparados com expectativas escritas explicitamente em prepare_tests.py.')
rows=[]
descriptions={'01_isa':('11 instruções; R0 gravável; LD/ST em FFF','R0=0001; R3=0007; R6=FFFF; RAM[FFF]=0007'),'02_branches':('Loop negativo; BEQ/BNE tomados e não tomados','R1=0000; R2=0003; R7=0000'),'03_limits':('SLT com sinal, overflow, imm -32/+31','R1=8000; R2=8000; R3=0001; R5=FFFF'),'04_offsets':('Deslocamentos de salto +31 e -32','R1=0001; R2=0007; R3=0009'),'05_random':('200 operações; semente fixa 20261030','R1=00D5; R2=00E8; R5=01E8; R6=0100'),'06_pc_wrap':('Incremento de PC em FFF','PC retorna a 000; R1=0001'),'07_branch_wrap':('BEQ -1 no endereço 000','Alvo FFF, seguido de JMP 001')}
for f in sorted((ROOT/'programs').glob('*.expected.json')):
    name=f.name.split('.')[0]; n=json.loads(f.read_text())['instructions']; desc,result=descriptions[name];rows.append([name+'\n'+str(n)+' instruções',desc,result])
table(['Programa','Objetivo','Resultado dirigido / esperado'],rows,[90,195,205])
p('<b>Modos.</b> Cada um dos sete programas roda com step sempre ativo e com step ativo uma vez a cada sete clocks. O segundo modo verifica retenção do estado durante pausas e ausência de escritas indevidas. Total: 268 instruções por modo, 536 comparações de aposentadoria no RTL.')
table(['Testbench adicional','Verificações'],[['tb_button','Bounce curto, pressão longa, soltura, segunda pressão e reset'],['tb_fault','Opcode inválido, retenção em FAULT, recuperação e reset durante execução'],['tb_top','Cinco apertos, PC=0001, RDM=520A, ULA=000A, SW17 e reset']],[100,390])
p('O teste top usa filtro reduzido para quatro ciclos; a configuração física usa 500000. O teste de bounce é digital e não substitui avaliação elétrica. Todos os testes têm asserções; o teste da CPU inclui timeout.',True)

title(7,'Resultados, discussão e uso de IA')
p('<b>Resultados executados em 30/10/2026.</b> GHDL 4.1.0, backend mcode, VHDL-2008: análise e elaboração aprovadas; 14 execuções da CPU mais três testbenches de suporte aprovados. Nenhuma asserção falhou na execução final. Os logs reais estão em results/ghdl.log e results/reference.log. O núcleo cpu_core também passou por ghdl --synth; o adaptador altsyncram não foi sintetizado por essa verificação.')
p('<b>Discussão.</b> A comparação a cada instrução detecta erros transitórios que poderiam desaparecer no valor final. Os testes de desvio distinguem claramente IP de PC já incrementado. O teste com pausas confirma que o ritmo humano não altera a semântica. Os casos de fronteira mostram a política modular de endereços e o comportamento de números negativos.')
p('<b>Limitações.</b> A bateria é finita, não uma prova formal. Não há medição de timing pós-roteamento, consumo, ocupação de LEs/M9Ks ou teste em hardware. A simulação usa modelo comportamental da memória, sem a biblioteca de simulação do fabricante; o adaptador altsyncram e o arquivo QSF ainda precisam ser compilados no Quartus. A pinagem considera a DE2-115 e seus jumpers padrão.')
p('<b>Dificuldades técnicas tratadas nesta implementação.</b> (1) A RAM síncrona exigiu estados de espera e captura separados. (2) O incremento antecipado do PC exigiu IP para saltos relativos. (3) Botão assíncrono exigiu sincronização, debounce e pulso único. (4) ST e desvios usam Ri como fonte, diferentemente das instruções aritméticas. (5) SLT compara operandos signed diretamente para não depender do sinal de uma subtração com overflow.')
p('<b>Dificuldade do ambiente.</b> O simulador não estava disponível inicialmente; uma cópia local de GHDL foi preparada para executar os testes. Quartus e FPGA não estavam disponíveis. Esses são registros da preparação assistida, não experiências atribuídas aos integrantes.')
p('<b>Uso de IA.</b> A IA foi usada para propor a arquitetura, escrever os módulos VHDL, o assembler, o modelo de referência, os programas, os testbenches, os arquivos de projeto e esta documentação. O objetivo foi produzir uma base completa e reproduzível. Também auxiliou na consulta à documentação da placa e na execução dos testes. O grupo deve revisar, compreender, adaptar e validar fisicamente o material, registrando suas contribuições reais.')
p('<b>Antes da entrega.</b> Acrescentar a compilação do Quartus e os resultados físicos na página seguinte; preencher integrantes; discutir divergências e dificuldades realmente vividas pelo grupo. Não converter os campos pendentes em afirmações de sucesso sem evidência.')

title(8,'Integração e validação na DE2-115')
p('Abrir quartus/cpu16.qpf; usar fpga_top e dispositivo EP4CE115F29C7. Manter apenas os arquivos rtl na síntese. A pinagem e os padrões de I/O foram preparados a partir do manual da placa; conferir JP7=2,5 V e JP6=3,3 V. A SDC define CLOCK_50 com período de 20 ns. [1]')
p('Compilar no Quartus, inspecionar warnings, memória inicializada e timing; gravar o .sof com USB-Blaster/JTAG. Após reset, KEY1 avança um estado; HEX3..0 mostram PC. SW17=0 seleciona RDM e SW17=1 seleciona ALUOut em HEX7..4. LEDs verdes indicam os nove estados. A tabela detalhada de pinagem está em quartus/de2_115_pins.qsf.')
table(['Aperto KEY1','LEDG','PC','RDM','ALUOut'],[['Reset','0','0000','0000','0000'],['1','1','0000','0000','0000'],['2','2','0001','520A','0000'],['3','3','0001','520A','0000'],['4','6','0001','520A','000A'],['5','0','0001','520A','000A']],[100,60,110,110,110])
p('Roteiro inicial com program.mif padrão. Os valores acima são esperados e também foram verificados em tb_top; ainda não são medições da placa. Apertos devem incluir soltura. No fim do programa, JMP 00E faz PC alternar entre 00E e 00F conforme o estado.',True)
table(['Registro físico a preencher pelo grupo','Situação atual'],[['Versão do Quartus, data e responsáveis','Pendente'],['Compilação, LEs, registradores e blocos de RAM','Pendente'],['Slack / Fmax e relatório de timing','Pendente'],['Fotos dos displays e estados','Pendente'],['Testes de LD/ST, desvios e botão na placa','Pendente'],['Problemas observados e alterações realizadas','Pendente']],[275,215])
p('<b>Referências e rastreabilidade.</b>',True)
p('[1] Terasic. DE2-115 User Manual, tabelas 4-1 a 4-5 e configuração dos jumpers. Consulta: 30/10/2026. https://www.terasic.com.tw/wiki/images/f/ff/DE2_115_User_manual_2013.pdf',True)
p('[2] Intel/Altera. Documentação de memória embarcada e altsyncram. Parâmetros SINGLE_PORT, largura, endereço, outdata_reg_a e init_file. Adaptador do projeto requer validação na biblioteca Quartus da instalação local. https://www.intel.com/programmable/technical-pdfs/683423.pdf',True)
p('[3] Enunciado do projeto fornecido pelo estudante. Logs e código-fonte desta implementação acompanham o pacote; convenções não determinadas pelo enunciado estão explicitadas nas páginas 2 a 5.',True)

def footer(c,doc):
    c.setStrokeColor(teal);c.line(42,40,553,40);c.setFont('CPUFont',8);c.setFillColor(grey)
    c.drawString(42,27,'CPU16 | Especificação técnica | 30/10/2026');c.drawRightString(553,27,str(doc.page))
doc=SimpleDocTemplate(str(OUT/'especificacao.pdf'),pagesize=(595.28,841.89),leftMargin=52,rightMargin=53,topMargin=42,bottomMargin=52,title='CPU16 - Especificação técnica',author='Projeto acadêmico com assistência de IA')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'especificacao.md').write_text('# CPU16 - Especificação técnica\n'+ '\n'.join(md))
print(OUT/'especificacao.pdf')
