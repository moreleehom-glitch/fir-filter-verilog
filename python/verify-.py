import matplotlib.pyplot as plt

def hex_to_signed(val, bits=16):
    val = int(val, 16)
    if val >= (1 << (bits - 1)):
        val -= (1 << bits)
    return val

def read_hex_file(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# 1. 读取所有文件
coeffs_hex = read_hex_file('coeff_hex.txt')
stim_hex   = read_hex_file('stimulus_hex.txt')
resp_hex   = read_hex_file('response_hex.txt')

N_taps     = len(coeffs_hex)
coeffs     = [hex_to_signed(c) for c in coeffs_hex]
stimulus   = [hex_to_signed(s) for s in stim_hex]
response_sim = [hex_to_signed(r, 32) for r in resp_hex]

# 2. Python 严格模拟 Verilog 行为 (32 位截断)
response_ideal = []
for t in range(len(stimulus)):
    acc = 0
    for k in range(N_taps):
        if t - k >= 0:
            x = stimulus[t - k]
            h = coeffs[k]
            prod = x * h
            prod = prod & 0xFFFFFFFF
            if prod >= 0x80000000: prod -= 0x100000000
            
            acc = acc + prod
            acc = acc & 0xFFFFFFFF
            if acc >= 0x80000000: acc -= 0x100000000
    response_ideal.append(acc)

# ★★★ 关键修改：对齐 Verilog 的 1 周期输出延迟 ★★★
# Verilog 在 DONE 状态才输出 acc，比理论计算晚 1 个时钟周期
# 所以仿真值 response_sim[t] 对应的是 理论值 response_ideal[t-1]
response_ideal_aligned = [0] + response_ideal[:-1]  # 右移 1 位，前面补 0

# 3. 对比结果（用对齐后的理论值）
match = True
max_err = 0
N_compare = min(len(response_sim), len(response_ideal_aligned))

for i in range(N_compare):
    err = abs(response_sim[i] - response_ideal_aligned[i])
    if err > max_err: max_err = err
    if response_sim[i] != response_ideal_aligned[i]:
        match = False

if match:
    print("✅ SUCCESS: Verilog 仿真结果与 Python 模型完全一致! (已对齐 1 周期延迟)")
else:
    print(f" 存在差异，最大误差: {max_err}")
    # 打印前 10 个不匹配样本
    for i in range(min(10, N_compare)):
        if response_sim[i] != response_ideal_aligned[i]:
            print(f"  索引 {i}: 仿真={response_sim[i]}, 理论(对齐)={response_ideal_aligned[i]}")

# 4. 画图保存
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(response_ideal, label='Python 理论值 (原始)', alpha=0.6)
plt.plot(response_sim, label='Verilog 仿真值', linestyle='--')
plt.legend()
plt.title('原始对比 (未对齐延迟)')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(response_ideal_aligned, label='Python 理论值 (右移 1 位对齐)', alpha=0.6, color='orange')
plt.plot(response_sim, label='Verilog 仿真值', linestyle='--')
plt.legend()
plt.title('对齐 1 周期延迟后对比')
plt.grid(True)

plt.tight_layout()
plt.savefig('verify_result.png', dpi=150)
print(" 对比图已保存为 verify_result.png")