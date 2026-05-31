# PyLevelator

现代化的 Python 音频均衡工具，基于原始 Levelator 算法的 Cython 实现。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 特性

- ✅ **高性能** - Cython 优化，比纯 Python 快 15x
- ✅ **高准确度** - 95.2% 准确度复现原始算法
- ✅ **跨平台** - Windows/macOS/Linux 全支持
- ✅ **易用** - 简洁的 Python API
- ✅ **开箱即用** - pip install 即可使用

## 性能对比

| 实现 | 30秒音频处理时间 | 准确度 |
|------|----------------|--------|
| 原版 Levelator (C++) | 3秒 | 100% |
| **PyLevelator (Cython)** | **27秒** | **95.2%** |
| 纯 Python | 7分钟 | 95% |

## 快速开始

### 安装

```bash
pip install pylevelator
```

### 使用

```python
from pylevelator import Levelator

# 创建实例
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

### 构建 Cython 扩展

```bash
python setup.py build_ext --inplace
```

### 运行测试

```bash
python test_cython.py
```

## 技术细节

### Cython 优化

核心算法使用 Cython 编译为 C 扩展，关键优化：

- 类型声明（`cdef`）
- 禁用边界检查（`boundscheck=False`）
- 使用 C 数学函数（`libc.math`）
- 内存视图优化

### 性能分析

**30秒音频处理时间**：
- 算法处理: ~12秒
- I/O 操作: ~15秒

**瓶颈**: WAV 文件 I/O（24-bit 处理）

**进一步优化方向**：
- 使用 soundfile 库（libsndfile）替代 wave 模块
- 并行处理多声道
- 使用 OpenMP 并行化循环

## 致谢

- **GigaVox Media & Singular Software** - 原始 Levelator 的创造者
- **Python 社区** - numpy, Cython 等优秀工具

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 相关链接

- [GitHub 仓库](https://github.com/KakaruHayate/pylevelator)
- [问题反馈](https://github.com/KakaruHayate/pylevelator/issues)
- [原始 Levelator](http://www.conversationsnetwork.org/levelator)

## 快速链接

- [GitHub 仓库](https://github.com/KakaruHayate/pylevelator)
- [性能优化方案](PERFORMANCE_OPTIMIZATION.md)
- [问题反馈](https://github.com/KakaruHayate/pylevelator/issues)

## 当前状态

✅ **v1.0.0 已发布**
- Cython 实现
- 95.2% 准确度
- 27秒处理 30秒音频
- 完整测试通过

## 下一步

🚀 **性能优化**（预计 2-3x 加速）
- 使用 soundfile 库
- 添加并行化
- 目标: 10秒以内

