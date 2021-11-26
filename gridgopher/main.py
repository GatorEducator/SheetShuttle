"""Entry point for the GridGopher tool. Implements CLI and plugin system."""

# pylint: disable=C0103
# pylint: disable=W0603

import typer

from pluginbase import PluginBase  # type: ignore[import]
from dotenv import load_dotenv

PLUGIN_BASE = PluginBase("gridgopher.plugins")

app = typer.Typer()

plugin_source = PLUGIN_BASE.make_plugin_source(searchpath=["plugins/"])
my_plugin = None


@app.command()
def gatorgopher(
    sheets_keys_file: str = typer.Option(
        ".env",
        "--sheets_keys_file",
        "-kf",
        help="Path to the Sheets api keys, either .json or .env file",
    ),
    sheets_config_directory: str = typer.Option(
        "config/sheet_sources",
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
    # TODO: remove this unnecessary print

    # NOTE: load_dotenv() has some problems when the .env file doesn't exist
    if sheets_keys_file.endswith(".env"):
        load_dotenv(dotenv_path=sheets_keys_file)
    print("Received arguments:")
    print(f"sheets_keys_file: {sheets_keys_file}")
    print(f"sheets_config_directory: {sheets_config_directory}")
    print(f"plugins_directory: {plugins_directory}")
    print(f"plugin_name: {plugin_name}")

    load_plugin(plugins_directory, plugin_name)
    # TODO: figure out how to pass the rest of the arguments
    my_plugin.run()


def load_plugin(directory: str, name: str):
    """Return a pluginbase object using a plugin name and a directory."""
    # TODO: add try statement for failed plugin loading and validating that a
    # run function exists in it.

    # TODO: not sure if "plugins" should be used here
    print(f"Loading {name} from {directory}...")
    global plugin_source
    plugin_source = PLUGIN_BASE.make_plugin_source(searchpath=[directory])
    global my_plugin
    my_plugin = plugin_source.load_plugin(name)


if __name__ == "__main__":
    app()
