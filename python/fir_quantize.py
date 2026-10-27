import numpy as np
from scipy.signal import firwin, freqz
import matplotlib.pyplot as plt

# ---- 1. 设计参数（和你之前一致）----
fs = 8000          # 采样率 8kHz
fc = 1000          # 截止频率 1kHz
N  = 64            # 阶数
beta = 8.0         # Kaiser β

# ---- 2. 浮点系数（你熟悉的 firwin）----
h_float = firwin(N+1, fc, fs=fs, window=('kaiser', beta))

# ---- 3. Q15 量化：乘 2^15 后四舍五入 ----
Q = 15
h_q15 = np.round(h_float * (2**Q)).astype(np.int32)

# ---- 4. 导出两种 Verilog 可读格式 ----
# (a) $readmemh 用的 hex 文件（有符号数用补码）
with open('coeff_hex.txt', 'w') as f:
    for c in h_q15:
        # 负数转 16 位补码
        f.write(f'{c & 0xFFFF:04X}\n')

# (b) 直接粘进 Verilog 的 parameter 数组（备选）
with open('coeff_param.txt', 'w') as f:
    f.write('parameter signed [15:0] COEFF [0:{}] = \'{{\n'.format(N))
    for i, c in enumerate(h_q15):
        comma = ',' if i < N else ''
        f.write(f'    16\'sd_{c}{comma}   // h[{i}] = {h_float[i]:+.6f}\n')
    f.write('};\n')

print(f'系数位宽范围: [{h_q15.min()}, {h_q15.max()}]')
print(f'已生成 coeff_hex.txt 和 coeff_param.txt')

# ---- 5. 关键：量化前后幅频响应对比 ----
# 这一张图就是你面试时说的"量化误差分析"
w_float, H_float = freqz(h_float, 1, worN=1024, fs=fs)
w_q15,   H_q15   = freqz(h_q15 / (2**Q), 1, worN=1024, fs=fs)

plt.figure(figsize=(9, 4))
plt.semilogy(w_float, np.abs(H_float), label='float', lw=2)
plt.semilogy(w_q15,   np.abs(H_q15),   label='Q15',  lw=2, ls='--')
plt.axvline(fc, color='k', ls=':', label=f'fc={fc}Hz')
plt.xlabel('Frequency (Hz)'); plt.ylabel('|H|')
plt.title(f'Kaiser FIR N={N}, β={beta}: float vs Q15')
plt.legend(); plt.grid(True, alpha=0.3)
plt.xlim(0, fs/2); plt.ylim(1e-6, 2)
plt.tight_layout()
plt.savefig('quantize_compare.png', dpi=150)
plt.show()

# ---- 6. 算一下阻带衰减损失了多少 dB ----
# 取阻带（>1.5*fc）区域的平均衰减
stopband = w_q15 > 1.5 * fc
A_float = -20*np.log10(np.max(np.abs(H_float[stopband])) + 1e-12)
A_q15   = -20*np.log10(np.max(np.abs(H_q15[stopband]))   + 1e-12)
print(f'浮点阻带衰减: {A_float:.1f} dB')
print(f'Q15 阻带衰减: {A_q15:.1f} dB')
print(f'量化损失:     {A_float - A_q15:.1f} dB  ← 这个数字面试会问')