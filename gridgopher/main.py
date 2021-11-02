"""Entry point for the GridGopher tool. Implements CLI and plugin system."""

import typer

from pluginbase import PluginBase


app = typer.Typer()


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
    print("Received arguments:")
    print(f"sheets_keys_file: {sheets_keys_file}")
    print(f"sheets_config_directory: {sheets_config_directory}")
    print(f"plugins_directory: {plugins_directory}")
    print(f"plugin_name: {plugin_name}")

    print(f"Loading {plugin_name} from {plugins_directory}...")
    # TODO: add try statement for failed plugin loading and validating that a
    # run function exists in it.

    # TODO: not sure if "plugins" should be used here
    plugin_base = PluginBase("plugins")
    plugin_source = plugin_base.make_plugin_source(searchpath=[plugins_directory])
    my_plugin = plugin_source.load_plugin(plugin_name)
    # TODO: figure out how to pass the rest of the arguments
    my_plugin.run()


if __name__ == "__main__":
    app()
