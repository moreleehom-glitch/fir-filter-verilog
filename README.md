# FIR Digital Filter - Verilog Fixed-Point Implementation (Q15)

## 📌 项目简介

本项目实现了一个基于 **Q15 定点格式** 的 FIR 数字滤波器，使用 Verilog HDL 编写，
并配套 Python 脚本完成系数量化、仿真验证与误差分析。

## 📁 目录结构

```
fir-filter-verilog/
── README.md
├── python/
│   ├── fir_quantize.py        # 系数量化脚本（浮点 → Q15）
│   ├── coeff_hex.txt          # Q15 系数（十六进制）
│   ├── coeff_param.txt        # Q15 系数（Verilog parameter 格式）
│   ├── verify.py              # Python vs Verilog 对比验证
│   ├── quantize_compare.png   # 量化误差对比图
│   └── verify_result.png      # 时域响应对比图
├── verilog/
│   ├── fir_q15.v              # FIR 顶层模块（Q15 定点）
│   ├── tb_fir.v               # Testbench 仿真文件
│   └── response_hex.txt       # Verilog 仿真输出
└── .gitignore
```

## 🛠 工具链

| 工具 | 用途 |
|------|------|
| Python 3.x + NumPy/Matplotlib | 系数量化、仿真对比 |
| Verilog 仿真器（ModelSim / Icarus / Vivado） | RTL 仿真验证 |

## 🚀 快速开始

### 1. 系数量化

```bash
cd python
python fir_quantize.py
```

生成 `coeff_hex.txt` 和 `coeff_param.txt`。

### 2. Verilog 仿真

将 `coeff_param.txt` 中的系数粘贴到 `fir_q15.v` 的 parameter 定义中，然后运行仿真：

```bash
# 使用 Icarus Verilog 示例
iverilog -o fir_sim verilog/fir_q15.v verilog/tb_fir.v
vvp fir_sim
```

仿真结果输出到 `verilog/response_hex.txt`。

### 3. 对比验证

```bash
cd python
python verify.py
```

生成 `quantize_compare.png`（量化误差）和 `verify_result.png`（时域对比）。

## 📊 设计参数

| 参数 | 值 |
|------|-----|
| 数据位宽 | 16-bit（Q15 格式） |
| 滤波器阶数 | N=64 |
| 采样率 | Fs=8kHz |
| 截止频率 | Fc=1kHz |

## 📄 License

MIT License
