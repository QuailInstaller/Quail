import os
import sys
import ctypes

def makedirs_ignore(*args, **kwargs):
    try:
        os.makedirs(*args, **kwargs)
    except FileExistsError:
        pass

def get_module_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_script():
    return os.path.realpath(sys.argv[0])


def get_script_name():
    return os.path.basename(get_script())


def get_script_path():
    return os.path.dirname(get_script())


def run_from_script():
    '''check if being run from script and not builded in standalone binary'''
    return get_script().endswith(".py")


def rerun_as_admin():
    if (platform.system() == 'Linux'):
        # os.system('pkexec %s %s' % (get_script_path(), ' '.join(sys.argv[1:])))
        raise NotImplementedError
    elif (platform.system() == 'Windows'):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None,
                                                'runas',
                                                sys.executable,
                                                ' '.join(sys.argv),
                                                None, 1)
    exit(0)
