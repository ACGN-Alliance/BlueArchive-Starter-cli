import click

__version__ = "0.0.1"

click.echo(f"欢迎使用BlueArchive-Starter-cli工具, 当前版本{__version__}")
click.confirm("再次回车以继续", abort=True, default=True)

click.echo("已结束")