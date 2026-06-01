"""
PyLevelator test suite — verifies the CLI and Levelator class.
"""

import sys
import time
from pathlib import Path

import numpy as np
import pytest


class TestLevelatorAPI:
    """Test the Levelator Python API."""

    def test_import(self):
        """Levelator and process can be imported from pylevelator."""
        from pylevelator import Levelator, process
        assert Levelator is not None
        assert process is not None

    def test_init_defaults(self):
        """Levelator initializes with correct defaults."""
        from pylevelator import Levelator
        lv = Levelator()
        assert lv.target_rms == 0.12
        assert lv.window_size == 0.5
        assert lv.smoothing == 0.3
        assert lv.max_gain == 20.0
        assert lv.min_gain == -10.0
        assert lv.lookahead == 0.1

    def test_init_custom(self):
        """Levelator accepts custom parameters."""
        from pylevelator import Levelator
        lv = Levelator(target_rms=0.15, max_gain=18.0, smoothing=0.4)
        assert lv.target_rms == 0.15
        assert lv.max_gain == 18.0
        assert lv.smoothing == 0.4

    def test_repr(self):
        """Levelator has a readable repr."""
        from pylevelator import Levelator
        lv = Levelator()
        r = repr(lv)
        assert "Levelator" in r
        assert "target_rms=0.12" in r

    def test_process_creates_file(self, tmp_path):
        """process() writes an output file."""
        from pylevelator import Levelator

        # Create a small test audio file
        sr = 44100
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr)).astype(np.float32)

        import soundfile as sf
        input_file = tmp_path / "test.wav"
        output_file = tmp_path / "out.wav"
        sf.write(str(input_file), audio, sr)

        lv = Levelator()
        result = lv.process(input_file, output_file)

        assert result.exists()
        assert result.stat().st_size > 0

    def test_process_default_output_name(self, tmp_path):
        """process() uses a default output name when output_file is None."""
        from pylevelator import Levelator

        sr = 44100
        audio = np.random.randn(sr).astype(np.float32) * 0.1

        import soundfile as sf
        input_file = tmp_path / "input.wav"
        sf.write(str(input_file), audio, sr)

        lv = Levelator()
        result = lv.process(input_file)

        assert result.name == "input.levelated.wav"

    def test_process_stereo(self, tmp_path):
        """process() handles stereo audio correctly."""
        from pylevelator import Levelator

        sr = 44100
        audio = np.column_stack([
            np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr)),
            np.sin(2 * np.pi * 523 * np.linspace(0, 1, sr)),
        ]).astype(np.float32)

        import soundfile as sf
        input_file = tmp_path / "stereo.wav"
        output_file = tmp_path / "stereo_out.wav"
        sf.write(str(input_file), audio, sr)

        lv = Levelator()
        result = lv.process(input_file, output_file)

        out_audio, out_sr = sf.read(str(result))
        assert out_audio.shape[1] == 2  # Still stereo

    def test_process_lookback_callback(self, tmp_path):
        """progress_callback is called with correct arguments."""
        from pylevelator import Levelator

        sr = 44100
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr)).astype(np.float32)

        import soundfile as sf
        input_file = tmp_path / "test.wav"
        sf.write(str(input_file), audio, sr)

        calls = []

        def callback(filename, percent):
            calls.append((filename, percent))

        lv = Levelator()
        lv.process(input_file, tmp_path / "out.wav", progress_callback=callback)

        filenames = {f for f, _ in calls}
        percents = [p for _, p in calls]
        assert input_file.name in filenames
        assert max(percents) == 100
        assert sorted(percents) == percents  # Non-decreasing

    def test_process_file_not_found(self):
        """process() raises FileNotFoundError for missing input."""
        from pylevelator import Levelator
        lv = Levelator()
        with pytest.raises(FileNotFoundError):
            lv.process("nonexistent.wav")

    def test_process_with_kwargs(self, tmp_path):
        """process() convenience function passes kwargs to Levelator."""
        from pylevelator import process

        sr = 44100
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr)).astype(np.float32)

        import soundfile as sf
        input_file = tmp_path / "test.wav"
        output_file = tmp_path / "out.wav"
        sf.write(str(input_file), audio, sr)

        result = process(input_file, output_file, target_rms=0.15)

        assert result.exists()


class TestCythonFunctions:
    """Test the Cython algorithm functions directly."""

    def test_compute_rms_envelope(self):
        """compute_rms_envelope returns a non-empty array."""
        from pylevelator._cython_impl import compute_rms_envelope

        audio = np.random.randn(44100).astype(np.float32) * 0.1
        window = 2048
        hop = 512

        rms = compute_rms_envelope(audio, window, hop)

        assert len(rms) > 0
        assert len(rms) < len(audio)
        assert rms.dtype == np.float32

    def test_compute_gain_curve(self):
        """compute_gain_curve returns gain values."""
        from pylevelator._cython_impl import compute_gain_curve

        rms = np.random.rand(1000).astype(np.float32) * 0.5 + 0.01

        gains = compute_gain_curve(rms, 0.12, 20.0, -10.0)

        assert len(gains) == len(rms)
        assert gains.dtype == np.float32

    def test_smooth_gains(self):
        """smooth_gains applies a moving average."""
        from pylevelator._cython_impl import smooth_gains

        gains = np.ones(1000, dtype=np.float32) * 5.0

        smoothed = smooth_gains(gains, 100)

        assert len(smoothed) == len(gains)

    def test_apply_gains(self):
        """apply_gains multiplies audio by gain values."""
        from pylevelator._cython_impl import apply_gains

        audio = np.sin(np.linspace(0, 6.28, 1000)).astype(np.float32)
        gains = np.ones(len(audio), dtype=np.float32) * 1.5

        processed = apply_gains(audio, gains)

        assert len(processed) == len(audio)
        assert processed.dtype == np.float32

    def test_apply_lookahead_limiter(self):
        """apply_lookahead_limiter reduces gain before peaks."""
        from pylevelator._cython_impl import apply_lookahead_limiter

        sr = 44100
        audio = np.sin(np.linspace(0, 6.28, sr)).astype(np.float32) * 0.5
        gains = np.ones(sr, dtype=np.float32) * 10.0
        lookahead_samples = int(0.1 * sr)

        limited = apply_lookahead_limiter(audio, gains, lookahead_samples, 0.98)

        assert len(limited) == len(gains)

    def test_full_pipeline_small(self, tmp_path):
        """End-to-end pipeline on a small synthetic audio file."""
        from pylevelator import Levelator

        sr = 44100
        # Mix of quiet and loud sections
        quiet = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, sr // 2)) * 0.01
        loud = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, sr // 2)) * 0.8
        audio = np.concatenate([quiet, loud]).astype(np.float32)

        import soundfile as sf
        input_file = tmp_path / "synth.wav"
        output_file = tmp_path / "synth_out.wav"
        sf.write(str(input_file), audio, sr)

        lv = Levelator()
        result = lv.process(input_file, output_file)

        assert result.exists()
        out_audio, out_sr = sf.read(str(result))
        assert len(out_audio) == len(audio)
        # Output should not be all zeros
        assert np.abs(out_audio).max() > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])