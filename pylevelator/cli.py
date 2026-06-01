"""
PyLevelator command-line interface.
"""

import click
from pathlib import Path
from pylevelator import Levelator, __version__


def _print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"PyLevelator {__version__}")
    ctx.exit()


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-i', '--input', 'input_path', required=True,
              type=click.Path(exists=True, path_type=Path),
              help='Input audio file or directory.')
@click.option('-o', '--output', 'output_path', required=True,
              type=click.Path(path_type=Path),
              help='Output audio file or directory.')
@click.option('--target-rms', default=0.12, show_default=True, type=float,
              help='Target RMS level (0.0 - 1.0).')
@click.option('--window-size', default=0.5, show_default=True, type=float,
              help='Analysis window size in seconds.')
@click.option('--smoothing', default=0.3, show_default=True, type=float,
              help='Gain smoothing window in seconds.')
@click.option('--max-gain', default=20.0, show_default=True, type=float,
              help='Maximum gain in dB.')
@click.option('--min-gain', default=-10.0, show_default=True, type=float,
              help='Minimum gain in dB.')
@click.option('--lookahead', default=0.1, show_default=True, type=float,
              help='Lookahead time in seconds.')
@click.option('--pattern', default='*.wav', show_default=True,
              help='Glob pattern for batch processing.')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output.')
@click.option('--version', is_flag=True, callback=_print_version,
              expose_value=False, is_eager=True, help='Show version and exit.')
def main(input_path, output_path, target_rms, window_size, smoothing,
         max_gain, min_gain, lookahead, pattern, verbose):
    """PyLevelator — Modern audio leveling tool.

    Single file:
        pylvl -i input.wav -o output.wav

    Batch mode:
        pylvl -i input_dir/ -o output_dir/
        pylvl -i input_dir/ -o output_dir/ --pattern "*.flac"
    """
    lv = Levelator(
        target_rms=target_rms,
        window_size=window_size,
        smoothing=smoothing,
        max_gain=max_gain,
        min_gain=min_gain,
        lookahead=lookahead,
    )

    if input_path.is_dir():
        files = sorted(input_path.glob(pattern))
        if not files:
            raise click.ClickException(
                f"No files matching '{pattern}' in {input_path}"
            )
        output_path.mkdir(parents=True, exist_ok=True)
        with click.progressbar(files, label='Processing') as bar:
            for f in bar:
                out_file = output_path / f.name
                lv.process(f, out_file)
                if verbose:
                    click.echo(f"  {f.name} -> {out_file}")
        click.echo(f"Done. {len(files)} file(s) processed.")
    else:
        lv.process(input_path, output_path)
        if verbose:
            click.echo(f"Done: {output_path}")
        else:
            click.echo(str(output_path))


if __name__ == '__main__':
    main()