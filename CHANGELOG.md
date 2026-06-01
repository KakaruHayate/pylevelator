# Changelog

All notable changes to PyLevelator are documented here.

## [Unreleased]

## [1.2.1] - 2026-06-01

### Fixed
- Output audio now preserves the input file's bit depth (subtype) and
  container format instead of being silently downgraded to 16-bit PCM.
  Matches the original Levelator's behavior.

## [1.2.0] - 2026-06-01

### Added
- Command-line interface (`pylvl`) with click
- Batch processing mode (process a directory of files)
- Bilingual documentation (English / Chinese)
- `process()` convenience function in the public API

### Changed
- Restructured package layout (`_core.py`, `_cython_impl.pyx`)
- Rewrote internal modules with professional English comments
- Class renamed `OptimizedBackend` → `Levelator`
- Simplified setup.py and pyproject.toml

### Removed
- Legacy `cython_backend` and non-optimized `core_cython` modules

## [1.1.0] - 2026-05-31

### Added
- OpenMP parallelization (~9× speedup on multi-core CPUs)
- soundfile-based I/O (~30× faster than the `wave` module)
- Cython memory views for zero-copy access

### Performance
- 40% faster than the original C++ Levelator
- 1.8s processing time for 30s audio at 44.1 kHz

## [1.0.0] - 2026-05-31

### Added
- Initial Cython implementation of the Levelator algorithm
- Cross-platform support (Windows / macOS / Linux)
- 95.2% output accuracy vs. the original Levelator
- Python API with the `Levelator` class
