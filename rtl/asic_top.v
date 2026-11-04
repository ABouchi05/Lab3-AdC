// SPDX-License-Identifier: SHL-0.51
// Logical macro terminals. No FPGA primitives, pad drivers or ESD cells.
module asic_top #(parameter Unified=0) (
 input wire clk_i, rst_ni,
 input wire [3:0] buttons_i,
 output wire [3:0] leds_o,
 output wire [6:0] segment1_o, segment2_o,
 input wire spi_sclk_i, spi_mosi_i, spi_cs_ni,
 output wire spi_miso_o
);
 // External reset: assert asynchronously; release synchronously to clk_i.
 pochoco_soc #(.Unified(Unified), .EnableSPI(1)) u_soc (
  .i_Clk(clk_i), .rst_ni(rst_ni), .i_Switch(buttons_i), .o_LED(leds_o),
  .o_Segment1_A(segment1_o[0]), .o_Segment1_B(segment1_o[1]),
  .o_Segment1_C(segment1_o[2]), .o_Segment1_D(segment1_o[3]),
  .o_Segment1_E(segment1_o[4]), .o_Segment1_F(segment1_o[5]), .o_Segment1_G(segment1_o[6]),
  .o_Segment2_A(segment2_o[0]), .o_Segment2_B(segment2_o[1]),
  .o_Segment2_C(segment2_o[2]), .o_Segment2_D(segment2_o[3]),
  .o_Segment2_E(segment2_o[4]), .o_Segment2_F(segment2_o[5]), .o_Segment2_G(segment2_o[6]),
  .i_SPI_SCLK(spi_sclk_i), .i_SPI_MOSI(spi_mosi_i),
  .i_SPI_CS_n(spi_cs_ni), .o_SPI_MISO(spi_miso_o)
 );
endmodule
