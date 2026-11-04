// SPDX-License-Identifier: SHL-0.51
module cycle_counter(input wire clk_i, rst_ni, output reg [31:0] cycles_o);
 always @(posedge clk_i or negedge rst_ni)
   if (!rst_ni) cycles_o <= 0;
   else cycles_o <= cycles_o + 1'b1;
endmodule
