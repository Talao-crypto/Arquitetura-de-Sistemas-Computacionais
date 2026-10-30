library ieee;
use ieee.std_logic_1164.all;
entity tb_top is end;
architecture test of tb_top is
  signal clk: std_logic := '0'; signal key: std_logic_vector(3 downto 0) := "1110";
  signal sw: std_logic_vector(17 downto 0) := (others=>'0');
  signal led: std_logic_vector(8 downto 0);
  signal h0,h1,h2,h3,h4,h5,h6,h7: std_logic_vector(6 downto 0);
begin
  clk <= not clk after 5 ns;
  dut: entity work.fpga_top generic map("programs/01_isa.hex",4)
    port map(clk,key,sw,led,h0,h1,h2,h3,h4,h5,h6,h7);
  process
    procedure cycles(n:positive) is begin for i in 1 to n loop wait until falling_edge(clk); end loop; end;
  begin
    cycles(3); key(0)<='1'; cycles(10);
    assert led="000000001" and h0="1000000" report "Top reset/display" severity failure;
    for i in 1 to 5 loop key(1)<='0'; cycles(12); key(1)<='1'; cycles(12); end loop;
    assert led="000000001" and h0="1111001" and h1="1000000" and h2="1000000" and h3="1000000"
      report "Top: cinco apertos / PC=0001" severity failure;
    -- RDM=520A, primeira instrucao.
    assert h7="0010010" and h6="0100100" and h5="1000000" and h4="0001000"
      report "Top: RDM / ordem dos HEX" severity failure;
    sw(17)<='1'; cycles(2);
    assert h7="1000000" and h6="1000000" and h5="1000000" and h4="0001000"
      report "Top: mux ULA=000A" severity failure;
    cycles(20); assert led="000000001" and h0="1111001" report "Top avancou sem botao" severity failure;
    key(0)<='0'; cycles(3);
    assert h0="1000000" and led="000000001" report "Top reset final" severity failure;
    report "PASS top: button, PC, RDM, ALU, displays, reset"; std.env.stop; wait;
  end process;
end;
