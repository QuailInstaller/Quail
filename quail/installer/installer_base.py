import os
import pathlib
import shutil
import atexit
import tempfile
import sys
from contextlib import suppress
from abc import ABC, abstractmethod
from .. import helper
from ..constants import Constants


def delete_atexit(to_delete):
    """On windows we can't remove binaries being run.
    This function will remove a file or folder at exit
    to be able to delete itself
    """

    def _delete_from_tmp():
        if not os.path.exists(to_delete) or os.path.isfile(to_delete):
            return
        tmpdir = tempfile.mkdtemp()
        newscript = shutil.copy2(helper.get_script(), tmpdir)
        args = (newscript, "--quail_rm", to_delete)
        if helper.running_from_script():
            os.execl(sys.executable, sys.executable, *args)
        else:
            os.execl(newscript, *args)

    atexit.register(_delete_from_tmp)


class InstallerBase(ABC):
    """Register application on the OS"""

    def __init__(self,
                 name,
                 binary,
                 icon,
                 publisher='Quail',
                 console=False,
                 launch_with_quail=True):
        self._launch_with_quail = launch_with_quail
        self._name = name
        self._binary_name = binary
        self._icon = icon
        self._publisher = publisher
        self._console = console
        self._install_path = self.build_install_path()
        self._solution_path = os.path.join(self._install_path, 'solution')

    def get_solution_icon(self):
        """Get solution's icon"""
        return self.get_solution_path(self._icon)

    @property
    def launch_with_quail(self):
        """Use quail to launch the binary
        (otherwise the shortcuts will launch the binary directly)
        """
        return self._launch_with_quail

    @property
    def quail_binary(self):
        """Get quail executable install path"""
        return self.get_install_path(helper.get_script_name())

    @property
    def launcher_binary(self):
        """Binary which will be launched by the main shortcut"""
        if self.launch_with_quail:
            return self.quail_binary
        return self.binary

    @property
    def binary(self):
        """Binary name (which must be at the root directory of your solution"""
        return self.get_solution_path(self._binary_name)

    @property
    def name(self):
        """Name of the program to be installed"""
        return self._name

    @property
    def publisher(self):
        """Information about who published the program"""
        return self._publisher

    @property
    def console(self):
        """Launch solution in console mode"""
        return self._console

    def build_install_path(self):
        """Build install path
        This function can be overriden to install files to somewhere else
        """
        return os.path.join(str(pathlib.Path.home()), '.quail', self.name)

    def get_solution_path(self, *args):
        """Get solution path"""
        return os.path.join(self._solution_path, *args)

    def get_install_path(self, *args):
        """Get install path"""
        return os.path.join(self._install_path, *args)

    @abstractmethod
    def register(self):
        os.makedirs(self.get_install_path(), exist_ok=True)
        # install script and module:
        shutil.copy2(helper.get_script(), self.quail_binary)
        if helper.running_from_script():
            shutil.copytree(helper.get_module_path(),
                            self.get_install_path("quail"))

    @abstractmethod
    def unregister(self):
        if helper.running_from_script():
            shutil.rmtree(self.get_install_path("quail"), ignore_errors=True)
            with suppress(FileNotFoundError):
                os.remove(self.quail_binary)
            with suppress(OSError):
                os.rmdir(self.get_install_path())
        else:
            # Assuming we can't remove our own binary
            delete_atexit(self.quail_binary)

    @abstractmethod
    def registered(self):
        return os.path.isfile(self.quail_binary)