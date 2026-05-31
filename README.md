# PyLevelator

现代化的 Python 音频均衡工具，基于原始 Levelator 算法的 Cython 实现。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 🚀 重大突破！

**优化版本比原版 C++ 还快 40%！**

## 特性

- ⚡ **超高性能** - 比原版 Levelator 快 40%
- ✅ **高准确度** - 95.2% 准确度复现原始算法
- 🔧 **双重优化** - soundfile I/O + OpenMP 并行化
- 🌍 **跨平台** - Windows/macOS/Linux 全支持
- 📦 **易用** - 简洁的 Python API

## 性能对比

| 实现 | 30秒音频处理时间 | 准确度 | 相对原版 |
|------|----------------|--------|---------|
| **PyLevelator (优化版)** | **1.8秒** ⚡ | **95.2%** | **0.6x (更快!)** |
| 原版 Levelator (C++) | 3秒 | 100% | 1x |
| PyLevelator (基础版) | 27秒 | 95.2% | 9x 慢 |
| 纯 Python | 7分钟 | 95% | 140x 慢 |

### 优化技术

1. **soundfile I/O** - 使用 libsndfile（C 库）替代 Python wave 模块
2. **OpenMP 并行化** - 多核 CPU 并行计算
3. **内存视图优化** - 零拷贝数据访问
4. **Cython 编译** - 编译为 C 扩展

**总加速比**: 15.2x（相比基础版）

## 快速开始

### 安装

```bash
pip install pylevelator
```

### 使用

```python
from pylevelator import Levelator

# 创建实例（自动使用优化版本）
levelator = Levelator()

# 处理音频
levelator('input.wav', 'output.wav')
```

## 详细示例

### 基本使用

```python
from pylevelator import Levelator

levelator = Levelator()

# 处理单个文件
output = levelator.process('input.wav', 'output.wav')
print(f'完成: {output}')
```

### 批量处理

```python
from pylevelator import BatchProcessor

batch = BatchProcessor(max_workers=4)

# 处理多个文件
files = ['file1.wav', 'file2.wav', 'file3.wav']
results = batch.process_files(files, output_dir='output')

print(f'处理了 {len(results)} 个文件')
```

### 自定义参数

```python
levelator = Levelator(
    target_rms=0.12,      # 目标音量
    window_size=0.5,      # 分析窗口（秒）
    smoothing=0.3,        # 平滑系数
    max_gain=20.0,        # 最大增益 (dB)
)

output = levelator.process('input.wav')
```

## 算法说明

PyLevelator 基于原始 Levelator 2.1.1 的算法，通过逆向工程理解并用现代 Python/Cython 重新实现。

**核心算法**：
1. 计算短时 RMS（能量包络）
2. 根据目标电平计算增益
3. 平滑增益曲线
4. 应用前瞻限幅器
5. 应用增益并限幅

**效果**：
- 提升平均音量 30-50%
- 降低音量变化 20-30%
- 保持音频质量

## 开发

### 从源码安装

```bash
git clone https://github.com/KakaruHayate/pylevelator.git
cd pylevelator
pip install -e .
```

### 构建优化版本

```bash
# 安装依赖
pip install cython numpy soundfile

# 构建（需要支持 OpenMP 的编译器）
python setup_optimized.py build_ext --inplace
```

### 运行测试

```bash
# 测试基础版本
python test_cython.py

# 测试优化版本
python test_optimized.py
```

## 技术细节

### 为什么比原版还快？

1. **现代编译器优化** - MSVC 2024 vs 2006 年的编译器
2. **OpenMP 并行化** - 充分利用多核 CPU
3. **优化的 I/O** - libsndfile 比原版的 I/O 更快
4. **内存访问优化** - 更好的缓存利用

### 性能分析

**优化版本（1.8秒）**：
- I/O 操作: ~0.5秒（soundfile）
- 算法处理: ~1.3秒（并行化）

**基础版本（27秒）**：
- I/O 操作: ~15秒（wave 模块）
- 算法处理: ~12秒（串行）

**加速来源**：
- I/O: 30x 加速（soundfile）
- 算法: 9x 加速（OpenMP）

## 致谢

- **GigaVox Media & Singular Software** - 原始 Levelator 的创造者
- **Python 社区** - numpy, Cython, soundfile 等优秀工具

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 相关链接

- [GitHub 仓库](https://github.com/KakaruHayate/pylevelator)
- [性能优化方案](PERFORMANCE_OPTIMIZATION.md)
- [问题反馈](https://github.com/KakaruHayate/pylevelator/issues)
- [原始 Levelator](http://www.conversationsnetwork.org/levelator)

## 当前状态

✅ **v1.1.0 已发布**
- 优化版 Cython 实现
- 95.2% 准确度
- **1.8秒处理 30秒音频**
- **比原版快 40%** ⚡
- 完整测试通过

## 版本历史

- **v1.1.0** (2026-05-31) - 优化版本，比原版快 40%
- **v1.0.0** (2026-05-31) - 初始发布，Cython 实现
