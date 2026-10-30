library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.cpu_pkg.all;
entity cpu_core is
  port(clk,reset,step: in std_logic;
       mem_q: in word_t; mem_addr: out std_logic_vector(11 downto 0);
       mem_data: out word_t; mem_we: out std_logic;
       pc_debug,rdm_debug,alu_debug,ir_debug: out word_t;
       leds: out std_logic_vector(8 downto 0);
       regs_debug: out std_logic_vector(127 downto 0));
end;
architecture rtl of cpu_core is
  signal state: state_t := FETCH_REQ;
  signal regs: regs_t := (others=>(others=>'0'));
  signal pc,ip: unsigned(11 downto 0) := (others=>'0');
  signal ir,a,b,rdm,alu_out,alu_b,alu_y: word_t := (others=>'0');
  signal op: natural range 0 to 15;
  signal ri,rj,rk: natural range 0 to 7;
begin
  op <= to_integer(unsigned(ir(15 downto 12)));
  ri <= to_integer(unsigned(ir(11 downto 9)));
  rj <= to_integer(unsigned(ir(8 downto 6)));
  rk <= to_integer(unsigned(ir(5 downto 3)));
  alu_b <= sext6(ir(5 downto 0)) when op=OP_ADDI or op=OP_LD or op=OP_ST else b;
  u_alu: entity work.alu port map(a,alu_b,op,alu_y);
  mem_addr <= alu_out(11 downto 0) when state=LOAD_WAIT or state=LOAD_CAPTURE or state=STORE_MEM
              else std_logic_vector(pc);
  mem_data <= b;
  mem_we <= '1' when state=STORE_MEM and step='1' and reset='0' else '0';
  pc_debug <= "0000" & std_logic_vector(pc);
  rdm_debug <= rdm; alu_debug <= alu_out; ir_debug <= ir;
  gen_debug: for i in 0 to 7 generate
    regs_debug(i*16+15 downto i*16) <= regs(i);
  end generate;
  process(state)
  begin
    leds <= (others=>'0'); leds(state_t'pos(state)) <= '1';
  end process;
  process(clk)
  begin
    if rising_edge(clk) then
      if reset='1' then
        regs <= (others=>(others=>'0')); pc <= (others=>'0'); ip <= (others=>'0');
        ir <= (others=>'0'); a <= (others=>'0'); b <= (others=>'0');
        rdm <= (others=>'0'); alu_out <= (others=>'0'); state <= FETCH_REQ;
      elsif step='1' then
        case state is
          when FETCH_REQ => state <= FETCH_LATCH;
          when FETCH_LATCH =>
            ir <= mem_q; rdm <= mem_q; ip <= pc; pc <= pc+1; state <= DECODE;
          when DECODE =>
            a <= regs(rj);
            if op=OP_ST or op=OP_BEQ or op=OP_BNE then b <= regs(ri);
            else b <= regs(rk); end if;
            state <= EXECUTE;
          when EXECUTE =>
            alu_out <= alu_y;
            case op is
              when OP_ADD | OP_SUB | OP_AND | OP_OR | OP_SLT | OP_ADDI => state <= WRITEBACK;
              when OP_LD => state <= LOAD_WAIT;
              when OP_ST => state <= STORE_MEM;
              when OP_BEQ | OP_BNE =>
                if (op=OP_BEQ and a=b) or (op=OP_BNE and a/=b) then
                  pc <= unsigned(signed(ip)+resize(signed(ir(5 downto 0)),12));
                end if;
                state <= FETCH_REQ;
              when OP_JMP => pc <= unsigned(ir(11 downto 0)); state <= FETCH_REQ;
              when others => state <= FAULT;
            end case;
          when LOAD_WAIT => state <= LOAD_CAPTURE;
          when LOAD_CAPTURE => rdm <= mem_q; state <= WRITEBACK;
          when WRITEBACK =>
            if op=OP_LD then regs(ri) <= rdm; else regs(ri) <= alu_out; end if;
            state <= FETCH_REQ;
          when STORE_MEM => state <= FETCH_REQ;
          when FAULT => null;
        end case;
      end if;
    end if;
  end process;
end;
