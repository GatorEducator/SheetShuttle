"""Entry point for the SheetShuttle tool. Implements CLI and plugin system."""

# pylint: disable=C0103
# pylint: disable=W0603

import json
from pathlib import Path
import typer

from pluginbase import PluginBase  # type: ignore[import]
from dotenv import load_dotenv

PLUGIN_BASE = PluginBase("sheetshuttle.plugins")

app = typer.Typer(name="sheetshuttle")

STANDARD_PLUGIN = '''""""Standard empty plugin for SheetShuttle."""

from sheetshuttle import github_objects
from sheetshuttle import sheet_collector

# This function is required
def run(sheets_keys_file, sheets_config_directory, gh_config_directory, **kwargs):
    """Standard run function."""
    pass
'''


@app.command("init", help="Create a plugin in the current directory.")
def init(
    plugin_name: str = typer.Argument(
        ...,
        help="Path to the Sheets api keys, either .json or .env file",
    ),
):
    """Genererate an empty plugin."""
    file_path = Path(plugin_name + ".py")
    if file_path.exists():
        print("ERROR: file already exists")
    with open(file_path, "w+", encoding="utf-8") as writefile:
        writefile.write(STANDARD_PLUGIN)
    print(f"{plugin_name} created successfully")


# pylint: disable=R0913
@app.command("run", help="Run sheetshuttle using your custom plugin.")
def sheetshuttle_run(
    sheets_keys_file: str = typer.Option(
        ".env",
        "--sheets-keys-file",
        "-kf",
        help="Path to the Sheets api keys, either .json or .env file",
    ),
    sheets_config_directory: str = typer.Option(
        "config/sheet_sources/",
        "--sheets-config-directory",
        "-sd",
        help="Directory to get the sheets configuration .yaml files from",
    ),
    gh_config_directory: str = typer.Option(
        "config/gh_sources/",
        "--gh-config-directory",
        "-gd",
        help="Directory to get the Github configuration .yaml files from",
    ),
    plugins_directory: str = typer.Option(
        "plugins/",
        "--plugins-directory",
        "-pd",
        help="Directory to get plugins from",
    ),
    plugin_name: str = typer.Option(
        "default",
        "--plugin-name",
        "-pn",
        help="Name of plugin to use for processing",
    ),
    json_args=typer.Option(
        None,
        "--json-args",
        "-ja",
        help="Path to the JSON file with additional arguments.",
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
    my_plugin.run(
        sheets_keys_file,
        sheets_config_directory,
        gh_config_directory,
        args=load_json_file(json_args),
    )


def load_plugin(directory: str, name: str):
    """Return a pluginbase object using a plugin name and a directory."""
    plugin_source = PLUGIN_BASE.make_plugin_source(searchpath=[directory])
    my_plugin = plugin_source.load_plugin(name)
    return plugin_source, my_plugin


def load_json_file(file_path):
    """Return the contents of a json file in the file path."""
    if not file_path:
        return {}
    try:
        with open(file_path, "r", encoding="uts-8") as read_file:
            data = json.load(read_file)
            return data
    except FileNotFoundError as error_obj:
        print(f"ERROR: JSON argument file '{file_path}' was not found.")
        raise error_obj


if __name__ == "__main__":
    app()
