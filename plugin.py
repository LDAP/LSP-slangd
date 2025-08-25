import os
import shutil
import stat
import sys
import tempfile
import zipfile
from typing import Dict
from urllib.request import urlopen

import sublime
from LSP.plugin import (
    AbstractPlugin,
    register_plugin,
    unregister_plugin,
)
from LSP.plugin.core.typing import Optional

from .modules.version import SLANG_VERSION

# Fix reloading for submodules
for m in list(sys.modules.keys()):
    if __package__ and m.startswith(__package__ + ".") and m != __name__:
        del sys.modules[m]


SESSION_NAME = "slangd"
STORAGE_DIR = "LSP-slangd"
SETTINGS_FILENAME = "LSP-slangd.sublime-settings"
VERSION_STRING = ".".join(str(s) for s in SLANG_VERSION)
GITHUB_DL_URL = (
    "https://github.com/shader-slang/slang/releases/download/"
    + "v{version}/slang-{version}-{platform}-{cpu_family}.zip"
)


def get_settings() -> sublime.Settings:
    return sublime.load_settings(SETTINGS_FILENAME)


def save_settings() -> None:
    return sublime.save_settings(SETTINGS_FILENAME)


def slangd_download_url():
    platform_str = sublime.platform()
    if platform_str == "osx":
        platform_str = "macos"

    arch = sublime.arch()
    if arch == "x64":
        cpu_family = "x86_64"
    elif arch == "arm64":
        cpu_family = "aarch64"
    else:
        raise OSError("unsupported cpu family")

    url = GITHUB_DL_URL.format(
        version=VERSION_STRING, platform=platform_str, cpu_family=cpu_family
    )
    return url


def download_file(url: str, file: str) -> None:
    with urlopen(url) as response, open(file, "wb") as out_file:
        shutil.copyfileobj(response, out_file)


def download_server(path: str):
    with tempfile.TemporaryDirectory() as tempdir:
        zip_path = os.path.join(tempdir, "server.zip")

        sublime.status_message("{}: Downloading server...".format(SESSION_NAME))
        download_file(slangd_download_url(), zip_path)

        sublime.status_message("{}: Extracting server...".format(SESSION_NAME))
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            extract_dir = os.path.join(
                path, "slangd_{version}".format(version=VERSION_STRING)
            )
            os.makedirs(extract_dir)
            zip_file.extractall(extract_dir)


class Clangd(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return SESSION_NAME

    @classmethod
    def storage_subpath(cls) -> str:
        return os.path.join(cls.storage_path(), STORAGE_DIR)

    @classmethod
    def managed_slangd_path(cls) -> Optional[str]:
        binary_name = "slangd.exe" if sublime.platform() == "windows" else "slangd"
        path = os.path.join(
            cls.storage_subpath(),
            "slangd_{version}/bin/{binary_name}".format(
                version=VERSION_STRING, binary_name=binary_name
            ),
        )
        if os.path.exists(path):
            return path
        return None

    @classmethod
    def system_slangd_path(cls, user_defined: str) -> Optional[str]:
        # Detect if slangd is installed or the command points to a valid binary.
        # Fallback, shutil.which has issues on Windows.
        system_binary_path = shutil.which(user_defined) or user_defined
        if not os.path.isfile(system_binary_path):
            return None
        return system_binary_path

    @classmethod
    def slangd_path(cls, user_defined: str) -> Optional[str]:
        """The command to start slangd"""
        if user_defined:
            return cls.system_slangd_path(user_defined)
        return cls.managed_slangd_path()

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        user_defined = get_settings().get("settings").get("slang.slangdLocation", "")
        if user_defined:
            return False
        return cls.slangd_path(user_defined) is None

    @classmethod
    def install_or_update(cls) -> None:
        if os.path.isdir(cls.storage_subpath()):
            shutil.rmtree(cls.storage_subpath())
        os.makedirs(cls.storage_subpath())
        download_server(cls.storage_subpath())

        # zip does not preserve file mode
        path = cls.managed_slangd_path()
        if not path:
            # this should never happen
            raise ValueError("installation failed silently")
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        user_defined = get_settings().get("settings").get("slang.slangdLocation", "")
        return {"server_path": cls.slangd_path(user_defined) or "slangd"}


def plugin_loaded() -> None:
    register_plugin(Clangd)


def plugin_unloaded() -> None:
    unregister_plugin(Clangd)
