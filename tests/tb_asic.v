`timescale 1ns/1ps
module tb;
 reg clk=0; always #50 clk=~clk;
 reg rst=0;
 reg [3:0] buttons=0;
 wire [3:0] leds;
 wire [6:0] s1,s2;
`ifndef UNIFIED
`define UNIFIED 0
`endif
`ifdef NETLIST
 asic_top dut (
`else
 asic_top #(.Unified(`UNIFIED)) dut (
`endif
 .clk_i(clk),.rst_ni(rst),.buttons_i(buttons),.leds_o(leds),
 .segment1_o(s1),.segment2_o(s2),
 .spi_sclk_i(1'b0),.spi_mosi_i(1'b0),.spi_cs_ni(1'b1));
 integer cycle=0, n, start_cycle, press_cycle, elapsed;
`ifdef GF180_NETLIST
 `include "tests/gf180_elapsed.vh"
`endif
 integer round_num, ticks, sum_ticks=0, changes=0;
 reg [3:0] target,last_target=0;
 reg [13:0] display_value;
 always @(posedge clk) cycle <= cycle+1;
 // Every cycle's observable outputs must match RTL and post-synthesis.
 integer trace;
 initial trace=$fopen("trace.csv","w");
 always @(negedge clk) $fdisplay(trace,"%0d,%h,%h,%h",cycle,leds,s1,s2);
 function [6:0] seg(input integer digit);
 begin case(digit)
 0:seg=~7'h3f; 1:seg=~7'h06; 2:seg=~7'h5b; 3:seg=~7'h4f;
 4:seg=~7'h66; 5:seg=~7'h6d; 6:seg=~7'h7d; 7:seg=~7'h07;
 8:seg=~7'h7f; 9:seg=~7'h6f; default:seg=~7'h79;
 endcase end endfunction
 task clocks(input integer count); begin repeat(count) @(negedge clk); end endtask
 task wait_led(input [3:0] value);
 begin n=0; while(leds!==value && n<50000) begin clocks(1); n=n+1; end
 if(n==50000) $fatal(1,"LED timeout %h",value); end endtask
 task wait_target;
 begin n=0; while(!(leds==1 || leds==2 || leds==4 || leds==8) && n<50000) begin clocks(1); n=n+1; end
 if(n==50000) $fatal(1,"Target timeout");
 target=leds; start_cycle=cycle;
 end endtask
 task correct_round(input integer delay_cycles);
 begin
 clocks(delay_cycles); press_cycle=cycle; buttons=target;
 clocks(150); buttons=0;
 // Two synchronizer stages, then capture: elapsed = delay + 3.
 elapsed=press_cycle-start_cycle+3; ticks=elapsed/1000;
`ifndef NETLIST
 if(dut.u_soc.u_periph.elapsed_q !== elapsed)
   $fatal(1,"Captured cycles differ: got=%0d expected=%0d",dut.u_soc.u_periph.elapsed_q,elapsed);
`endif
`ifdef GF180_NETLIST
 if(gf180_captured_cycles !== elapsed)
   $fatal(1,"Mapped capture differs: got=%0d expected=%0d",gf180_captured_cycles,elapsed);
`endif
 sum_ticks=sum_ticks+ticks;
 wait_led(0);
 if(s1!==seg(ticks/10) || s2!==seg(ticks%10)) $fatal(1,"Incorrect reaction display");
 $display("MEASURE start=%0d press=%0d elapsed=%0d ticks=%0d",start_cycle,press_cycle,elapsed,ticks);
 end endtask
 initial begin
 clocks(5); rst=1;
 wait_led(15); clocks(2900);
 if(leds!==15) $fatal(1,"Wait shorter than configured");
 wait_target;
 clocks(1600); buttons=15; clocks(150); buttons=0;
 wait_led(0);
 if(s1!==seg(14) || s2!==seg(14)) $fatal(1,"Missing EE");
 wait_led(15);
 $display("PASS incorrect press repeats round");
 for(round_num=0;round_num<10;round_num=round_num+1) begin
   wait_target;
   if(target!=last_target) changes=changes+1;
   last_target=target;
   correct_round(1500+round_num*127);
   if(round_num<9) wait_led(15);
 end
 clocks(5000); ticks=sum_ticks/10;
 if(s1!==seg(ticks/10) || s2!==seg(ticks%10)) $fatal(1,"Incorrect average");
 if(changes<2) $fatal(1,"Target does not vary");
 buttons=1; clocks(500); buttons=0; wait_led(15);
 $display("PASS 10 rounds, average, restart");
 $fclose(trace); $finish;
 end
 initial begin #50000000; $fatal(1,"Global timeout"); end
endmodule
