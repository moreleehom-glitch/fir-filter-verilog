module fir_q15 #(
    parameter N       = 64,
    parameter COEFF_W = 16,
    parameter DATA_W  = 16,
    parameter ACC_W   = 32
)(
    input  wire             clk,
    input  wire             rst_n,
    input  wire             en,
    input  wire signed [DATA_W-1:0]  din,
    output reg  signed [ACC_W-1:0]   dout
);

    reg signed [COEFF_W-1:0] coeff [0:N];
    integer i;
    initial begin
        $readmemh("coeff_hex.txt", coeff);
    end

    reg signed [DATA_W-1:0] shift_reg [0:N];

    localparam IDLE  = 2'b00;
    localparam SHIFT = 2'b01;
    localparam MAC   = 2'b10;
    localparam DONE  = 2'b11;

    reg [1:0] state;
    reg [$clog2(N+1)-1:0] mac_idx;
    reg signed [ACC_W-1:0] acc;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state   <= IDLE;
            mac_idx <= 0;
            acc     <= 0;
            dout    <= 0;
            for (i = 0; i <= N; i = i + 1)
                shift_reg[i] <= 0;
        end else begin
            case (state)
                IDLE: begin
                    if (en) begin
                        for (i = N; i > 0; i = i - 1)
                            shift_reg[i] <= shift_reg[i-1];
                        shift_reg[0] <= din;
                        state <= SHIFT;
                    end
                end
                SHIFT: begin
                    mac_idx <= 0;
                    acc     <= 0;
                    state   <= MAC;
                end
                MAC: begin
                    acc <= acc + shift_reg[mac_idx] * coeff[mac_idx];
                    if (mac_idx == N)
                        state <= DONE;
                    else
                        mac_idx <= mac_idx + 1;
                end
                DONE: begin
                    dout  <= acc;
                    state <= IDLE;
                end
                default: state <= IDLE;
            endcase
        end
    end
endmodule