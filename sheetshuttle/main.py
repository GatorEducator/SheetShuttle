"""Entry point for the SheetShuttle tool. Implements CLI and plugin system."""

# pylint: disable=C0103
# pylint: disable=W0603

import typer

from pluginbase import PluginBase  # type: ignore[import]
from dotenv import load_dotenv

PLUGIN_BASE = PluginBase("sheetshuttle.plugins")

app = typer.Typer()


@app.command()
def sheetshuttle(
    sheets_keys_file: str = typer.Option(
        ".env",
        "--sheets_keys_file",
        "-kf",
        help="Path to the Sheets api keys, either .json or .env file",
    ),
    sheets_config_directory: str = typer.Option(
        "config/sheet_sources/",
        "--sheets_config_directory",
        "-cd",
        help="Directory to get the sheets configuration .yaml files from",
    ),
    plugins_directory: str = typer.Option(
        "plugins/",
        "--plugins_directory",
        "-pd",
        help="Directory to get plugins from",
    ),
    plugin_name: str = typer.Option(
        "default",
        "--plugin_name",
        "-pn",
        help="Name of plugin to use for processing",
    ),
):
    """Create the CLI and runs the chosen plugin."""
    if sheets_keys_file.endswith(".env"):
        load_dotenv(dotenv_path=sheets_keys_file)
    _, my_plugin = load_plugin(plugins_directory, plugin_name)
    methods_list = [
        func for func in dir(my_plugin) if callable(getattr(my_plugin, func))
    ]
    if "run" not in methods_list:
        raise Exception(f"ERROR: function run was not found in {plugin_name} plugin.")
    my_plugin.run(sheets_keys_file, sheets_config_directory)


def load_plugin(directory: str, name: str):
    """Return a pluginbase object using a plugin name and a directory."""
    plugin_source = PLUGIN_BASE.make_plugin_source(searchpath=[directory])
    my_plugin = plugin_source.load_plugin(name)
    return plugin_source, my_plugin


if __name__ == "__main__":
    app()
