// SPDX-License-Identifier: SHL-0.51
// ASIC replacement of the group's SB_RAM40_4K register file.
module espino_register_file (
 input wire clk_i, rst_ni,
 input wire [3:0] raddr_a_i, raddr_b_i,
 output reg [31:0] rdata_a_o, rdata_b_o,
 input wire [3:0] waddr_i,
 input wire [31:0] wdata_i,
 input wire we_i
);
 reg [31:0] registers [1:15];
 integer i;
 always @(posedge clk_i or negedge rst_ni) begin
   if (!rst_ni) begin
     rdata_a_o <= 0; rdata_b_o <= 0;
     for (i=1;i<16;i=i+1) registers[i] <= 0;
   end else begin
     // Read-before-write, as in the original synchronous BRAM.
     rdata_a_o <= raddr_a_i == 0 ? 32'b0 : registers[raddr_a_i];
     rdata_b_o <= raddr_b_i == 0 ? 32'b0 : registers[raddr_b_i];
     if (we_i && waddr_i != 0) registers[waddr_i] <= wdata_i;
   end
 end
endmodule
