"""
PyLevelator CLI tests — verifies the pylvl command-line interface.
"""

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest


class TestCLI:
    """Test the pylvl CLI via subprocess."""

    def _run(self, *args, **kwargs):
        """Run pylvl CLI with given arguments, return CompletedProcess."""
        import subprocess
        # Run from a directory with no .wav files to avoid MSVCRT glob
        # expansion of pattern arguments on Windows.
        kwargs.setdefault('cwd', str(Path(sys.executable).parent))
        return subprocess.run(
            [sys.executable, "-m", "pylevelator.cli"] + list(args),
            capture_output=True,
            text=True,
            **kwargs,
        )

    def _make_wav(self, tmp_path, name="test.wav", duration=1.0, sr=44100):
        """Create a synthetic WAV file for testing."""
        import soundfile as sf
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration))).astype(np.float32)
        path = tmp_path / name
        sf.write(str(path), audio, sr)
        return path

    def test_help(self):
        """pylvl --help exits with 0 and shows usage."""
        result = self._run("--help")
        assert result.returncode == 0
        assert "PyLevelator" in result.stdout or "Usage" in result.stdout

    def test_version(self):
        """pylvl --version shows the version."""
        result = self._run("--version")
        assert result.returncode == 0
        assert "1.2.0" in result.stdout

    def test_missing_input(self):
        """pylvl without required options exits with error."""
        result = self._run("-i", "nonexistent.wav", "-o", "out.wav")
        assert result.returncode != 0

    def test_input_file_not_found(self, tmp_path):
        """pylvl with non-existent input file shows an error."""
        result = self._run(
            "-i", str(tmp_path / "nonexistent.wav"),
            "-o", str(tmp_path / "out.wav"),
        )
        assert result.returncode != 0
        # Click rejects the path before our code runs ("does not exist")
        combined = (result.stdout + result.stderr).lower()
        assert "not exist" in combined or "not found" in combined

    def test_single_file(self, tmp_path):
        """pylvl processes a single audio file correctly."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run("-i", str(input_file), "-o", str(output_file))

        assert result.returncode == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_single_file_verbose(self, tmp_path):
        """pylvl -v prints progress output."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run("-i", str(input_file), "-o", str(output_file), "-v")

        assert result.returncode == 0
        # Should mention the output file when verbose
        combined = result.stdout + result.stderr
        assert "wav" in combined.lower() or "processing" in combined.lower()

    def test_custom_target_rms(self, tmp_path):
        """pylvl accepts --target-rms."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run(
            "-i", str(input_file),
            "-o", str(output_file),
            "--target-rms", "0.15",
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_custom_window_size(self, tmp_path):
        """pylvl accepts --window-size."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run(
            "-i", str(input_file),
            "-o", str(output_file),
            "--window-size", "0.3",
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_custom_smoothing(self, tmp_path):
        """pylvl accepts --smoothing."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run(
            "-i", str(input_file),
            "-o", str(output_file),
            "--smoothing", "0.5",
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_custom_gain_limits(self, tmp_path):
        """pylvl accepts --max-gain and --min-gain."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run(
            "-i", str(input_file),
            "-o", str(output_file),
            "--max-gain", "15.0",
            "--min-gain", "-5.0",
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_custom_lookahead(self, tmp_path):
        """pylvl accepts --lookahead."""
        input_file = self._make_wav(tmp_path)
        output_file = tmp_path / "out.wav"

        result = self._run(
            "-i", str(input_file),
            "-o", str(output_file),
            "--lookahead", "0.05",
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_batch_directory(self, tmp_path):
        """pylvl processes all matching files in a directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create 3 test files
        for i in range(3):
            self._make_wav(input_dir, f"test_{i}.wav")

        result = self._run(
            "-i", str(input_dir),
            "-o", str(output_dir),
        )

        assert result.returncode == 0
        for i in range(3):
            assert (output_dir / f"test_{i}.wav").exists()

    def test_batch_with_pattern(self, tmp_path):
        """pylvl respects --pattern in batch mode."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        self._make_wav(input_dir, "match.wav")
        # Create a non-matching file
        import soundfile as sf
        audio = np.zeros(44100, dtype=np.float32)
        sf.write(str(input_dir / "skip.flac"), audio, 44100)

        result = self._run(
            "-i", str(input_dir),
            "-o", str(output_dir),
            "--pattern", "*.wav",
        )

        assert result.returncode == 0
        assert (output_dir / "match.wav").exists()
        assert not (output_dir / "skip.flac").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])