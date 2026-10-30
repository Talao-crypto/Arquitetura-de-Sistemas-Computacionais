library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
use std.textio.all;
architecture simulation of memory_sync is
  type ram_t is array(0 to 4095) of std_logic_vector(15 downto 0);
  impure function initialize return ram_t is
    file f: text open read_mode is INIT_FILE;
    variable l: line; variable m: ram_t := (others=>x"F000");
    variable i: natural := 0;
  begin
    while not endfile(f) loop
      assert i<4096 report "Image too large" severity failure;
      readline(f,l); hread(l,m(i)); i:=i+1;
    end loop;
    return m;
  end;
  signal ram: ram_t := initialize;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if we='1' then ram(to_integer(unsigned(addr))) <= data; q <= data;
      else q <= ram(to_integer(unsigned(addr))); end if;
    end if;
  end process;
end;
