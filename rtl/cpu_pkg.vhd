library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
package cpu_pkg is
  subtype word_t is std_logic_vector(15 downto 0);
  type regs_t is array (0 to 7) of word_t;
  type state_t is (FETCH_REQ, FETCH_LATCH, DECODE, EXECUTE,
                  LOAD_WAIT, LOAD_CAPTURE, WRITEBACK, STORE_MEM, FAULT);
  constant OP_ADD : natural := 0;
  constant OP_SUB : natural := 1;
  constant OP_AND : natural := 2;
  constant OP_OR  : natural := 3;
  constant OP_SLT : natural := 4;
  constant OP_ADDI: natural := 5;
  constant OP_LD  : natural := 6;
  constant OP_ST  : natural := 7;
  constant OP_BEQ : natural := 8;
  constant OP_BNE : natural := 9;
  constant OP_JMP : natural := 10;
  function sext6(x : std_logic_vector(5 downto 0)) return word_t;
end package;
package body cpu_pkg is
  function sext6(x : std_logic_vector(5 downto 0)) return word_t is
  begin return std_logic_vector(resize(signed(x),16)); end;
end package body;
