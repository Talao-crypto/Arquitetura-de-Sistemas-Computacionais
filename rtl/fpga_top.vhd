library ieee;
use ieee.std_logic_1164.all;
use work.cpu_pkg.all;
entity fpga_top is
  generic(INIT_FILE: string := "program.mif"; DEBOUNCE_CYCLES: positive := 500000);
  port(CLOCK_50: in std_logic; KEY: in std_logic_vector(3 downto 0);
       SW: in std_logic_vector(17 downto 0); LEDG: out std_logic_vector(8 downto 0);
       HEX0,HEX1,HEX2,HEX3,HEX4,HEX5,HEX6,HEX7: out std_logic_vector(6 downto 0));
end;
architecture rtl of fpga_top is
  signal reset_pipe: std_logic_vector(1 downto 0) := "11";
  signal reset,step,we: std_logic;
  signal addr: std_logic_vector(11 downto 0);
  signal q,data,pc,rdm,result,display: word_t;
begin
  -- Asynchronous assertion, synchronous reset release; KEY0 active low.
  process(CLOCK_50,KEY(0))
  begin
    if KEY(0)='0' then reset_pipe <= "11";
    elsif rising_edge(CLOCK_50) then reset_pipe <= reset_pipe(0) & '0'; end if;
  end process;
  reset <= reset_pipe(1);
  button: entity work.step_button generic map(DEBOUNCE_CYCLES)
    port map(CLOCK_50,reset,KEY(1),step);
  cpu: entity work.cpu_core port map(CLOCK_50,reset,step,q,addr,data,we,pc,rdm,result,open,LEDG,open);
  ram: entity work.memory_sync generic map(INIT_FILE) port map(CLOCK_50,we,addr,data,q);
  display <= rdm when SW(17)='0' else result;
  h0: entity work.hex7 port map(pc(3 downto 0),HEX0);
  h1: entity work.hex7 port map(pc(7 downto 4),HEX1);
  h2: entity work.hex7 port map(pc(11 downto 8),HEX2);
  h3: entity work.hex7 port map(pc(15 downto 12),HEX3);
  h4: entity work.hex7 port map(display(3 downto 0),HEX4);
  h5: entity work.hex7 port map(display(7 downto 4),HEX5);
  h6: entity work.hex7 port map(display(11 downto 8),HEX6);
  h7: entity work.hex7 port map(display(15 downto 12),HEX7);
end;
