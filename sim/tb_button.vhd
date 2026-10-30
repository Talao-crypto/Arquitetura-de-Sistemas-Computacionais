library ieee;
use ieee.std_logic_1164.all;
entity tb_button is end;
architecture test of tb_button is
  signal clk: std_logic := '0'; signal reset: std_logic := '1';
  signal key_n: std_logic := '1'; signal pulse: std_logic;
  signal pulses: natural := 0;
begin
  clk <= not clk after 5 ns;
  dut: entity work.step_button generic map(4) port map(clk,reset,key_n,pulse);
  process(clk)
    variable previous: std_logic := '0';
  begin
    if rising_edge(clk) then
      if reset='1' then pulses<=0; previous:='0';
      else
        assert not(pulse='1' and previous='1') report "Pulso longo" severity failure;
        if pulse='1' then pulses<=pulses+1; end if;
        previous:=pulse;
      end if;
    end if;
  end process;
  process
    procedure cycles(n:positive) is begin for i in 1 to n loop wait until falling_edge(clk); end loop; end;
  begin
    cycles(2); reset<='0'; cycles(2);
    key_n<='0'; cycles(1); key_n<='1'; cycles(1); key_n<='0'; cycles(1); key_n<='1'; cycles(10);
    assert pulses=0 report "Bounce produziu pulso" severity failure;
    key_n<='0'; cycles(20);
    assert pulses=1 report "Pressao longa nao gerou exatamente um pulso" severity failure;
    key_n<='1'; cycles(1); key_n<='0'; cycles(1); key_n<='1'; cycles(12);
    assert pulses=1 report "Soltar gerou pulso" severity failure;
    key_n<='0'; cycles(12);
    assert pulses=2 report "Segunda pressao perdida" severity failure;
    reset<='1'; cycles(2); key_n<='1'; reset<='0'; cycles(12);
    assert pulses=0 report "Reset falhou" severity failure;
    report "PASS debounce: bounce, hold, release, second press, reset";
    std.env.stop; wait;
  end process;
end;
