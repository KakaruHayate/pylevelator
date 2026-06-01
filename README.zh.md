# PyLevelator

**[English](README.md)**

经典音频均衡工具 [Levelator](https://appdb.winehq.org/appview.php?iAppId=8618) 的现代 Python
实现，提供命令行和 Python API。

## 特性

- **快速** — 比原版 C++ Levelator 快约 40%（30s 音频：1.8s vs 3.0s）
- **跨平台** — Windows、macOS、Linux；Python 3.8+
- **易于安装** — `pip install pylevelator`
- **可调参数** — 可自定义 RMS 目标、增益限制、平滑窗口、前瞻时间
- **CLI + API** — 可从命令行使用，也可作为库集成

## 性能

测试条件：30 秒音频（44.1 kHz，单声道，Intel i7，8 线程）：

| 实现方式 | 耗时 | 相对速度 |
|----------|------|----------|
| 原版 Levelator（C++, 2010） | 3.0s | 1.0× |
| **PyLevelator（本项目）** | **1.8s** | **1.7× 更快** |

## 工作原理

PyLevelator 通过五个阶段对音频进行处理，使整段录音的响度保持一致：

1. **RMS 包络计算** — 用滑动窗口（默认 0.5 秒）遍历音频，计算每个位置的均方根能量。
   这给出了音频在每个时刻的"响度"的平滑表示。

2. **增益曲线计算** — 对每个采样点，计算需要多少增益（dB）才能将局部 RMS 提升到
   目标水平。增益会被限制在 `[min_gain, max_gain]` 范围内（默认：`[-10 dB, +20 dB]`）。

3. **增益平滑** — 对增益曲线施加移动平均滤波（默认 0.3 秒），使相邻采样点之间的
   增益不会突变。如果没有这一步，输出会听起来"断断续续"。

4. **前瞻限幅** — 向前扫描，预先在峰值到来之前降低增益，避免数字削波。
   削减量会均匀分布在前方的前瞻窗口内（默认 0.1 秒）。这是 Levelator 听起来自然的
   关键：它在峰值到来之前就做出反应，而非事后处理。

5. **增益应用** — 将每个音频采样点乘以对应的增益值，并将输出硬限幅在 `±0.99`。

最终效果：安静的部分被合理提升，响亮的部分被温和压低，整体录音响度一致，
不会出现普通压缩器那种"喘息"感。

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install pylevelator
```

提供 Python 3.8–3.11 在 Windows、macOS（arm64 + x86_64）、Linux 上的预编译 wheels。

### 从源码安装

需要支持 OpenMP 的 C 编译器：
- **Windows** — MSVC（Visual Studio 2019+）
- **macOS** — libomp（`brew install libomp`）
- **Linux** — GCC（含 libgomp）

```bash
git clone https://github.com/KakaruHayate/pylevelator.git
cd pylevelator
pip install .
```

## 快速开始

### 命令行

```bash
pylvl -i input.wav -o output.wav
pylvl -i input.wav -o output.wav --target-rms 0.15
pylvl -i input_dir/ -o output_dir/
pylvl --help
```

### Python API

```python
from pylevelator import Levelator, process

# 基本用法
lv = Levelator()
lv.process("input.wav", "output.wav")

# 自定义参数
lv = Levelator(target_rms=0.15, max_gain=18.0, smoothing=0.4)
lv.process("input.wav", "output.wav")

# 一行调用
process("input.wav", "output.wav", target_rms=0.15)
```

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-i, --input` | 必填 | 输入音频文件或目录 |
| `-o, --output` | 必填 | 输出音频文件或目录 |
| `--target-rms` | 0.12 | 目标 RMS 电平（0.0–1.0） |
| `--window-size` | 0.5 | 分析窗口大小（秒） |
| `--smoothing` | 0.3 | 增益平滑窗口（秒） |
| `--max-gain` | 20.0 | 最大增益（dB） |
| `--min-gain` | −10.0 | 最小增益（dB） |
| `--lookahead` | 0.1 | 前瞻时间（秒） |
| `--pattern` | `*.wav` | 批量处理的文件匹配模式 |
| `-v, --verbose` | 关闭 | 详细输出 |

## 参数调优指南

- **`target-rms`** — 目标响度，越高 = 整体越响。
  - 播客/人声：0.15–0.20（更响亮）
  - 音乐/动态内容：0.08–0.12（保留动态）
  - 默认 0.12 约等于 −18 dBFS。

- **`window-size`** — 算法对音量变化的响应速度。
  - 较小（0.2–0.3s）：更快、更激进
  - 较大（0.5–1.0s）：更慢、更平滑、保留动态

- **`smoothing`** — 增益过渡的平滑程度。
  - 较大（0.4–0.6s）：更少突变，可能感觉迟缓
  - 较小（0.1–0.2s）：响应更快，但可能不够自然

- **`max-gain` / `min-gain`** — 安全边界。
  - 如果提升的安静部分出现噪声，降低 `max-gain`。
  - 如果想保留更多原有动态，提升 `min_gain`。

- **`lookahead`** — 前瞻限幅器的时间窗口。
  - 较大（0.15–0.2s）：更多削波保护，响应稍慢
  - 较小（0.05–0.1s）：更快，裕量更少

## 支持的格式

PyLevelator 使用 [soundfile](https://github.com/bastibe/python-soundfile) 进行 I/O，
支持：**WAV**、**FLAC**、**OGG**、**AIFF**、**CAF** 等。
输出格式自动与输入格式保持一致。

## 许可证

MIT — 参见 [LICENSE](LICENSE)。
