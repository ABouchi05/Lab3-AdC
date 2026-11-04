`timescale 1ns/1ps
module tb_alu;
 reg [31:0] a,b;
 reg [3:0] op;
 wire [31:0] result;
 wire cmp;
 reg [31:0] expected;
 reg expected_cmp;
 integer i,k;
 espino_alu dut(op,a,b,result,cmp);
 initial begin
 for(i=0;i<2000;i=i+1) begin
   a=$random; b=$random;
   if(i==0) begin a=32'hffffffff;b=1;end
   for(k=0;k<16;k=k+1) begin
     op=k; expected_cmp=0;
     case(k)
     0:expected=a+b;1:expected=a-b;2:expected=a^b;3:expected=a|b;4:expected=a&b;
     8:expected=$signed(a)<$signed(b);9:expected=a<b;
     default:expected=a+b;
     endcase
     case(k)
     10:expected_cmp=a==b;11:expected_cmp=a!=b;
     12:expected_cmp=$signed(a)<$signed(b);13:expected_cmp=$signed(a)>=$signed(b);
     14:expected_cmp=a<b;15:expected_cmp=a>=b;
     endcase
     #1;
     if(result!==expected || cmp!==expected_cmp) $fatal(1,"ALU mismatch op=%0d",k);
   end
 end
 $display("PASS ALU: 32000 vectors including overflow and signed compares");$finish;
 end
endmodule
