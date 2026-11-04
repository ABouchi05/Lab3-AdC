`timescale 1ns/1ps
module tb_memory;
 reg clk=0; always #5 clk=~clk;
 reg rst=0, ar=0, br=0, we=0;
 reg [31:0] aa=0, ba=0, wd=0;
 reg [3:0] be=0;
 wire [31:0] ai0,ai1,rd0,rd1;
 asic_memory #(.Unified(0)) rom(clk,rst,ar,aa,ai0,br,we,be,ba,wd,rd0);
 asic_memory #(.Unified(1)) ff(clk,rst,ar,aa,ai1,br,we,be,ba,wd,rd1);
 task tick; begin @(negedge clk); end endtask
 initial begin
 tick; tick; rst=1; ar=1;
 tick;
 if(ai0!==32'h80000137 || ai1!==ai0) $fatal(1,"Boot image/reset");
 ba=396; br=1; we=1; be=15; wd=32'h12345678;
 tick; we=0; tick;
 if(rd0!==wd || rd1!==wd) $fatal(1,"Scratch write");
 we=1; be=4'b0010; wd=32'h0000ab00; tick; we=0; tick;
 if(rd0!==32'h1234ab78 || rd1!==rd0) $fatal(1,"Byte enable");
 ba=0; we=1; be=15; wd=32'hdeadbeef; tick; we=0; tick;
 if(ai1!==wd || ai0!==32'h80000137) $fatal(1,"Writable unified vs protected ROM");
 aa=32'h10000; ba=32'h10000; tick;
 if(ai0!==32'h13 || ai1!==32'h13 || rd0!==0 || rd1!==0) $fatal(1,"Address alias");
 rst=0; tick; rst=1; aa=0; ba=396; tick;
 if(ai0!==32'h80000137 || ai1!==ai0 || rd0!==0 || rd1!==0) $fatal(1,"Reset reload");
 $display("PASS memory reset, byte enables, ROM protection, unified writes, bounds");
 $finish;
 end
endmodule
