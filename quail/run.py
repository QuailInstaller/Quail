import sys
import argparse
import shutil
import os
from contextlib import suppress
from .constants import Constants
from . import helper
from .builder import Builder
from .manager import Manager
from .controller import ControllerConsole

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(Constants.ARGUMENT_UNINSTALL,
                        help="uninstall program",
                        action="store_true")
    parser.add_argument(Constants.ARGUMENT_BUILD,
                        help="build executable",
                        action="store_true")
    parser.add_argument(Constants.ARGUMENT_RM,
                        type=str,
                        help="""remove file or folder:
                        if file is passed as argument and the file's directory
                        is empty, the directory will be removed
                        (this function is used by quail for windows uninstall)
                        """)
    return parser.parse_args()


def run(solution, installer, builder=None, controller=None):
    """run config"""
    args = parse_args()
    if not builder:
        builder = Builder()
    if not controller:
        controller = ControllerConsole()
    manager = Manager(installer, solution, builder)
    if args.quail_rm:
        shutil.rmtree(args.quail_rm)
    elif args.quail_build:
        manager.build()
    elif args.quail_uninstall:
        controller.start_uninstall(manager)
    else:
        if manager.is_installed():
            if manager.new_version_available():
                controller.start_update(manager)
            manager.run()
        else:
            controller.start_install(manager)
