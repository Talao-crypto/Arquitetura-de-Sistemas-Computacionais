library ieee;
use ieee.std_logic_1164.all;
entity memory_sync is
  generic(INIT_FILE: string := "program.mif");
  port(clk,we: in std_logic; addr: in std_logic_vector(11 downto 0);
       data: in std_logic_vector(15 downto 0); q: out std_logic_vector(15 downto 0));
end;
