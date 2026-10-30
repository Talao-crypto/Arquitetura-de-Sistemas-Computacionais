library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.cpu_pkg.all;
entity alu is
  port(a,b: in word_t; op: in natural range 0 to 15; y: out word_t);
end;
architecture rtl of alu is
begin
  process(a,b,op)
  begin
    y <= (others=>'0');
    case op is
      when OP_ADD | OP_ADDI | OP_LD | OP_ST => y <= std_logic_vector(unsigned(a)+unsigned(b));
      when OP_SUB | OP_BEQ | OP_BNE => y <= std_logic_vector(unsigned(a)-unsigned(b));
      when OP_AND => y <= a and b;
      when OP_OR => y <= a or b;
      when OP_SLT => if signed(a)<signed(b) then y <= x"0001"; end if;
      when others => null;
    end case;
  end process;
end;
