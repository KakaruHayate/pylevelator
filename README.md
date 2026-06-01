# PyLevelator

**[中文文档](README.zh.md)**

A modern Python implementation of the [Levelator](https://en.wikipedia.org/wiki/The_Levelator)
audio leveling tool, with a command-line interface and Python API.

## Features

- **Fast** — ~40% faster than the original C++ Levelator (1.8s vs 3.0s for 30s audio)
- **Cross-platform** — Windows, macOS, Linux; Python 3.8+
- **Easy to install** — `pip install pylevelator`
- **Configurable** — tune RMS target, gain limits, smoothing, lookahead
- **CLI + API** — use from the command line or integrate as a library

## Performance

Benchmarked on 30s audio (44.1 kHz, mono, Intel i7, 8 threads):

| Implementation | Time | Relative |
|----------------|------|----------|
| Original Levelator (C++, 2010) | 3.0s | 1.0× |
| **PyLevelator** | **1.8s** | **1.7× faster** |

## How It Works

PyLevelator processes audio through five stages to balance loudness:

1. **RMS Envelope Calculation** — slides a window (default: 0.5s) over the audio and
   computes the root-mean-square energy at each position. This gives a smoothed
   representation of how loud the audio is at every moment.

2. **Gain Curve Calculation** — at each sample, computes how much gain (in dB) is
   needed to bring the local RMS up to the target level. Gain is clamped to the
   `[min_gain, max_gain]` range (default: `[-10 dB, +20 dB]`).

3. **Gain Smoothing** — applies a moving-average filter (default: 0.3s) to the gain
   curve so that adjacent samples don't jump abruptly. Without this, the output
   would sound "choppy" or "pumping".

4. **Lookahead Limiting** — scans forward in time and pre-emptively reduces gain
   before any peak that would exceed the clipping threshold. The reduction is spread
   over the preceding lookahead window (default: 0.1s). This is the key step that
   makes Levelator sound natural — it reacts to peaks before they happen rather than
   after.

5. **Gain Application** — multiplies each audio sample by its corresponding gain
   value and hard-limits the output to `±0.99` to prevent digital clipping.

The result: quiet passages are boosted, loud passages are gently tamed, and the
overall recording feels consistently loud without the "pumping" artifacts of
simple compressors.

## Installation

### From PyPI (recommended)

```bash
pip install pylevelator
```

Pre-built wheels for Python 3.8–3.11 on Windows, macOS (arm64 + x86_64), and Linux.

### From source

Requires a C compiler with OpenMP support:
- **Windows** — MSVC (Visual Studio 2019+)
- **macOS** — libomp (`brew install libomp`)
- **Linux** — GCC with `libgomp`

```bash
git clone https://github.com/KakaruHayate/pylevelator.git
cd pylevelator
pip install .
```

## Quick Start

### Command line

```bash
pylvl -i input.wav -o output.wav
pylvl -i input.wav -o output.wav --target-rms 0.15
pylvl -i input_dir/ -o output_dir/
pylvl --help
```

### Python API

```python
from pylevelator import Levelator, process

# Basic usage
lv = Levelator()
lv.process("input.wav", "output.wav")

# Custom parameters
lv = Levelator(target_rms=0.15, max_gain=18.0, smoothing=0.4)
lv.process("input.wav", "output.wav")

# One-liner
process("input.wav", "output.wav", target_rms=0.15)
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i, --input` | required | Input audio file or directory |
| `-o, --output` | required | Output audio file or directory |
| `--target-rms` | 0.12 | Target RMS level (0.0–1.0) |
| `--window-size` | 0.5 | Analysis window in seconds |
| `--smoothing` | 0.3 | Gain smoothing window in seconds |
| `--max-gain` | 20.0 | Maximum gain in dB |
| `--min-gain` | −10.0 | Minimum gain in dB |
| `--lookahead` | 0.1 | Lookahead time in seconds |
| `--pattern` | `*.wav` | File pattern for batch mode |
| `-v, --verbose` | off | Verbose output |

## Parameter Guide

- **`target-rms`** — target loudness level. Higher = louder output.
  - Podcasts / voice: 0.15–0.20 (louder)
  - Music / dynamic content: 0.08–0.12 (preserve dynamics)
  - Default (0.12) is roughly −18 dBFS.

- **`window-size`** — how quickly the algorithm reacts to volume changes.
  - Smaller (0.2–0.3s): faster, more aggressive
  - Larger (0.5–1.0s): slower, smoother, preserves dynamics

- **`smoothing`** — how smooth the gain transitions are.
  - Larger (0.4–0.6s): fewer abrupt changes, may feel sluggish
  - Smaller (0.1–0.2s): quicker response, may sound less natural

- **`max-gain` / `min-gain`** — safety rails.
  - Lower `max-gain` if you hear noise in boosted quiet sections.
  - Raise `min-gain` if you want to preserve the original dynamics more.

- **`lookahead`** — time window for the peak limiter.
  - Larger (0.15–0.2s): more clipping protection, slightly slower response
  - Smaller (0.05–0.1s): snappier, less headroom

## Supported Formats

PyLevelator uses [soundfile](https://github.com/bastibe/python-soundfile) for I/O,
supporting: **WAV**, **FLAC**, **OGG**, **AIFF**, **CAF**, and more.
The output format matches the input format automatically.

## License

MIT — see [LICENSE](LICENSE).
