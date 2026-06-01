"""
PyLevelator core — Python wrapper around the Cython algorithm.

Provides the Levelator class and a process() convenience function.
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Union, Optional, Callable

from pylevelator._cython_impl import (
    compute_rms_envelope,
    compute_gain_curve,
    smooth_gains,
    apply_gains,
    apply_lookahead_limiter,
)

__all__ = ["Levelator", "process"]


class Levelator:
    """
    Audio leveling processor.

    Balances the loudness of an audio recording by applying adaptive gain at each
    point to bring the local energy toward a target RMS level, then smoothing the
    result to avoid abrupt volume jumps.

    Args:
        target_rms: Target RMS amplitude, typically 0.08–0.20.
                    Higher = louder output. Default: 0.12 (~-18 dBFS).
        window_size: Analysis window length in seconds. Default: 0.5.
        smoothing: Gain smoothing window in seconds. Default: 0.3.
        max_gain: Maximum allowed gain boost in dB. Default: 20.0.
        min_gain: Maximum allowed gain cut in dB. Default: -10.0.
        lookahead: Lookahead time in seconds for the peak limiter. Default: 0.1.
    """

    def __init__(
        self,
        target_rms: float = 0.12,
        window_size: float = 0.5,
        smoothing: float = 0.3,
        max_gain: float = 20.0,
        min_gain: float = -10.0,
        lookahead: float = 0.1,
    ):
        self.target_rms = target_rms
        self.window_size = window_size
        self.smoothing = smoothing
        self.max_gain = max_gain
        self.min_gain = min_gain
        self.lookahead = lookahead

    def process(
        self,
        input_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Process an audio file and write the leveled output.

        Args:
            input_file: Path to the input audio file. Supports WAV, FLAC, OGG, etc.
            output_file: Path for the output file. Defaults to <input_stem>.levelated<ext>.
            progress_callback: Optional callable(filename, percent) for progress updates.

        Returns:
            Path to the output file.
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        output_path = (
            Path(output_file)
            if output_file is not None
            else input_path.parent / f"{input_path.stem}.levelated{input_path.suffix}"
        )

        filename = input_path.name

        # Stage 1: read audio via soundfile (30x faster than the wave module)
        if progress_callback:
            progress_callback(filename, 5)
        info = sf.info(str(input_path))
        audio, sr = sf.read(str(input_path), dtype='float32')

        # Convert multi-channel to mono for analysis
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1).astype(np.float32)
        else:
            audio_mono = audio.astype(np.float32)

        if progress_callback:
            progress_callback(filename, 10)

        # Stage 2: compute RMS envelope (parallelized)
        window_samples = int(self.window_size * sr)
        hop_samples = window_samples // 4
        rms_values = compute_rms_envelope(audio_mono, window_samples, hop_samples)

        # Interpolate RMS values back to the original sample rate
        rms_envelope = np.interp(
            np.arange(len(audio_mono)),
            np.arange(len(rms_values)) * hop_samples + window_samples // 2,
            rms_values,
        ).astype(np.float32)

        if progress_callback:
            progress_callback(filename, 40)

        # Stage 3: compute gain curve (parallelized)
        gain_curve = compute_gain_curve(
            rms_envelope,
            self.target_rms,
            self.max_gain,
            self.min_gain,
        )

        if progress_callback:
            progress_callback(filename, 60)

        # Stage 4: smooth the gain curve (parallelized)
        smoothing_samples = int(self.smoothing * sr)
        if smoothing_samples > 1:
            gain_curve = smooth_gains(gain_curve, smoothing_samples)

        if progress_callback:
            progress_callback(filename, 75)

        # Stage 5: lookahead peak limiting (sequential)
        lookahead_samples = int(self.lookahead * sr)
        if lookahead_samples > 0:
            gain_curve = apply_lookahead_limiter(
                audio_mono,
                gain_curve,
                lookahead_samples,
                0.98,
            )

        if progress_callback:
            progress_callback(filename, 90)

        # Stage 6: apply gains to the audio (parallelized)
        if len(audio.shape) > 1:
            audio_processed = np.zeros_like(audio)
            for ch in range(audio.shape[1]):
                audio_processed[:, ch] = apply_gains(
                    audio[:, ch].astype(np.float32), gain_curve
                )
        else:
            audio_processed = apply_gains(audio_mono, gain_curve)

        # Stage 7: write output via soundfile, preserving the original
        # format and bit depth (subtype) so the file matches the input.
        sf.write(
            str(output_path),
            audio_processed,
            sr,
            subtype=info.subtype,
            format=info.format,
        )

        if progress_callback:
            progress_callback(filename, 100)

        return output_path

    def __repr__(self) -> str:
        return (
            f"Levelator(target_rms={self.target_rms}, window_size={self.window_size}, "
            f"smoothing={self.smoothing}, max_gain={self.max_gain}, "
            f"min_gain={self.min_gain}, lookahead={self.lookahead})"
        )


def process(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    **kwargs,
) -> Path:
    """
    Convenience function: create a Levelator with the given parameters and process a file.

    All keyword arguments are passed to Levelator.__init__.

    Examples:
        from pylevelator import process
        process("input.wav", "output.wav")
        process("in.wav", "out.wav", target_rms=0.15, max_gain=18.0)
    """
    return Levelator(**kwargs).process(input_file, output_file)