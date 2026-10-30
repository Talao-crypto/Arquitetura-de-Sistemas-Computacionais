library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
use std.textio.all;
use work.cpu_pkg.all;
entity tb_cpu is
  generic(IMAGE: string := "programs/01_isa.hex";
          TRACE: string := "programs/01_isa.trace";
          PAUSED: boolean := false);
end;
architecture test of tb_cpu is
  signal clk: std_logic := '0';
  signal reset: std_logic := '1'; signal step: std_logic := '0';
  signal we: std_logic; signal addr: std_logic_vector(11 downto 0);
  signal data,q,pc,rdm,result,ir: word_t;
  signal regs: std_logic_vector(127 downto 0);
  signal leds: std_logic_vector(8 downto 0);
begin
  clk <= not clk after 5 ns;
  dut: entity work.cpu_core port map(clk,reset,step,q,addr,data,we,pc,rdm,result,ir,leds,regs);
  ram: entity work.memory_sync(simulation) generic map(IMAGE) port map(clk,we,addr,data,q);
  process
    file f: text open read_mode is TRACE;
    variable l: line; variable expected: word_t;
    variable oldled: std_logic_vector(8 downto 0);
    variable oldregs: std_logic_vector(127 downto 0);
    variable oldpc,oldrdm,oldalu,oldir: word_t;
    variable write_addr: word_t := x"FFFF"; variable write_data: word_t := x"0000";
    variable count: natural := 0;
  begin
    wait until falling_edge(clk); wait until falling_edge(clk); reset <= '0';
    for cycle in 0 to 30000 loop
      if PAUSED and cycle mod 7/=0 then step <= '0'; else step <= '1'; end if;
      wait until rising_edge(clk);
      oldled:=leds; oldregs:=regs; oldpc:=pc; oldrdm:=rdm; oldalu:=result; oldir:=ir;
      if we='1' then
        assert write_addr=x"FFFF" report "Mais de uma escrita por instrucao" severity failure;
        write_addr:="0000"&addr; write_data:=data;
      end if;
      wait for 1 ns;
      if step='0' then
        assert regs=oldregs and leds=oldled and pc=oldpc and rdm=oldrdm and result=oldalu and ir=oldir
          report "Estado mudou durante pausa" severity failure;
        assert we='0' report "Escrita durante pausa" severity failure;
      end if;
      assert leds(8)='0' report "Opcode invalido inesperado" severity failure;
      if leds(0)='1' and oldled(0)='0' then
        assert not endfile(f) report "Trace curta" severity failure;
        readline(f,l); hread(l,expected);
        assert pc=expected report "PC divergente instrucao "&integer'image(count) severity failure;
        for r in 0 to 7 loop
          hread(l,expected);
          assert regs(r*16+15 downto r*16)=expected
            report "Registrador R"&integer'image(r)&" divergente instrucao "&integer'image(count) severity failure;
        end loop;
        hread(l,expected); assert write_addr=expected report "Endereco ST divergente" severity failure;
        hread(l,expected); assert write_data=expected report "Dado ST divergente" severity failure;
        write_addr:=x"FFFF"; write_data:=x"0000"; count:=count+1;
        if endfile(f) then
          report "PASS CPU "&IMAGE&" instrucoes="&integer'image(count)&" paused="&boolean'image(PAUSED);
          std.env.stop; wait;
        end if;
      end if;
      wait until falling_edge(clk);
    end loop;
    assert false report "Timeout" severity failure; wait;
  end process;
end;
