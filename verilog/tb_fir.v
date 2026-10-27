`timescale 1ns/1ps
module tb_fir;
    reg clk, rst_n, en;
    reg signed [15:0] din;
    wire signed [31:0] dout;

    // 实例化你的 FIR 滤波器
    fir_q15 #(.N(64)) uut (
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en),
        .din(din), 
        .dout(dout)
    );

    // 产生 100MHz 时钟 (周期 10ns)
    initial clk = 0;
    always #5 clk = ~clk;

    // 激励数据和文件句柄
    reg signed [15:0] stim_data [0:255];
    integer i;
    integer resp_fd;

    initial begin
        rst_n = 0; en = 0; din = 0;
        #20 rst_n = 1;  // 复位 20ns 后释放

        // 读取 Python 生成的激励文件
        $readmemh("stimulus_hex.txt", stim_data);
        
        // 打开输出文件
        resp_fd = $fopen("response_hex.txt", "w");

        // 逐个发送 256 个样本
        for (i = 0; i < 256; i = i + 1) begin
            @(posedge clk);
            din = stim_data[i];
            en = 1;           // 拉高 en，告诉滤波器有新数据
            @(posedge clk);
            en = 0;           // 一个周期后拉低
            
            // 单 MAC 串行架构，处理一个样本需要 N+2 = 66 个时钟周期
            // 等待 66 个周期后，dout 就是当前样本的滤波结果
            repeat (66) @(posedge clk);
            
            // 把结果写入文件 (Q30 格式)
            $fwrite(resp_fd, "%h\n", dout);
        end
        
        #100 $finish;  // 仿真结束
    end
endmodule