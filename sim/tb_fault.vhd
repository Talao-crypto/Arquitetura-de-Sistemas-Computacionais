library ieee;
use ieee.std_logic_1164.all;
use work.cpu_pkg.all;
entity tb_fault is end;
architecture test of tb_fault is
  signal clk: std_logic := '0'; signal reset: std_logic := '1';
  signal step: std_logic := '1'; signal q: word_t := x"F000";
  signal we: std_logic; signal addr: std_logic_vector(11 downto 0);
  signal data,pc,rdm,result,ir: word_t; signal leds: std_logic_vector(8 downto 0);
  signal regs: std_logic_vector(127 downto 0);
begin
  clk <= not clk after 5 ns;
  dut: entity work.cpu_core port map(clk,reset,step,q,addr,data,we,pc,rdm,result,ir,leds,regs);
  process
    procedure cycles(n:positive) is begin for i in 1 to n loop wait until falling_edge(clk); end loop; end;
  begin
    cycles(2); reset<='0'; cycles(10);
    assert leds(8)='1' and we='0' and pc=x"0001" report "FAULT falhou" severity failure;
    cycles(10); assert leds(8)='1' and pc=x"0001" report "FAULT nao reteve estado" severity failure;
    reset<='1'; cycles(2);
    assert pc=x"0000" and leds(0)='1' and regs=(regs'range=>'0') report "Reset falhou" severity failure;
    reset<='0'; q<=x"523F"; cycles(5); -- ADDI R1,R0,-1
    assert regs(31 downto 16)=x"FFFF" report "Recuperacao apos reset falhou" severity failure;
    -- Reset durante instrucao em andamento.
    cycles(2); reset<='1'; cycles(1);
    assert pc=x"0000" and regs=(regs'range=>'0') report "Reset em voo falhou" severity failure;
    report "PASS fault and reset"; std.env.stop; wait;
  end process;
end;
