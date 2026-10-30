library ieee;
use ieee.std_logic_1164.all;
library altera_mf;
use altera_mf.altera_mf_components.all;
architecture quartus of memory_sync is
begin
  ram: altsyncram
    generic map(intended_device_family=>"Cyclone IV E", operation_mode=>"SINGLE_PORT", width_a=>16, widthad_a=>12,
      numwords_a=>4096, width_byteena_a=>1, outdata_reg_a=>"UNREGISTERED",
      init_file=>INIT_FILE, lpm_type=>"altsyncram",
      read_during_write_mode_port_a=>"NEW_DATA_NO_NBE_READ")
    port map(clock0=>clk, address_a=>addr, data_a=>data, wren_a=>we,
      byteena_a=>"1", clocken0=>'1', q_a=>q);
end;
