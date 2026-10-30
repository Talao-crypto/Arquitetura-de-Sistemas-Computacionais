#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build results
python3 tools/prepare_tests.py | tee results/reference.log
GHDL=${GHDL:-ghdl}
"$GHDL" -a --std=08 --workdir=build rtl/cpu_pkg.vhd rtl/alu.vhd rtl/cpu_core.vhd rtl/step_button.vhd rtl/hex7.vhd rtl/memory_sync.vhd sim/memory_sim.vhd rtl/fpga_top.vhd sim/tb_cpu.vhd sim/tb_button.vhd sim/tb_fault.vhd sim/tb_top.vhd
{
  for tb in tb_button tb_fault tb_top; do
    "$GHDL" -e --std=08 --workdir=build "$tb"
    "$GHDL" -r --std=08 --workdir=build "$tb" --assert-level=error
  done
  "$GHDL" -e --std=08 --workdir=build tb_cpu
  for f in programs/*.asm; do
    stem=${f%.asm}
    for paused in false true; do
      "$GHDL" -r --std=08 --workdir=build tb_cpu -gIMAGE="$stem.hex" -gTRACE="$stem.trace" -gPAUSED="$paused" --assert-level=error
    done
  done
} | tee results/ghdl.log
