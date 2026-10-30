library ieee;
use ieee.std_logic_1164.all;
entity step_button is
  generic(STABLE_CYCLES: positive := 500000);
  port(clk,reset,key_n: in std_logic; pulse: out std_logic);
end;
architecture rtl of step_button is
  signal sync1,sync2,stable: std_logic := '1';
  signal count: natural range 0 to STABLE_CYCLES-1 := 0;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      pulse <= '0';
      if reset='1' then
        sync1 <= '1'; sync2 <= '1'; stable <= '1'; count <= 0;
      else
        sync1 <= key_n; sync2 <= sync1;
        if sync2=stable then count <= 0;
        elsif count=STABLE_CYCLES-1 then
          stable <= sync2; count <= 0;
          if sync2='0' then pulse <= '1'; end if;
        else count <= count+1;
        end if;
      end if;
    end if;
  end process;
end;
