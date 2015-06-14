from errno import EEXIST
from logging import getLogger
from os import getcwd, unlink
from os.path import join, realpath, isfile

from psutil import Process, NoSuchProcess
from funcy import decorator

from .exceptions import InvalidPidFileError, PidFileExistsError

logger = getLogger(__name__)
default_location = realpath(join(getcwd(), '.pid'))


@decorator
def one(call, pid_directory=default_location):
    """ Check if the call is already running. If so, bail out. If not, create a
    file that contains the process identifier (PID) and creation time. After call
    has completed, remove the process information file.
    :param call: The original function using the @one decorator.
    :param pid_directory: The name of the directory where the process information will be written.
    :return: The output of the original function.
    """
    if _is_running(pid_directory):
        logger.info('The process is already running.')
        return

    _set_running(pid_directory)
    try:
        result = call()
    finally:
        _delete(pid_directory)
    return result


def _is_running(directory):
    """ Determine whether or not the process is currently running.
    :param directory: The PID directory containing the process information.
    :return: Whether or not the process is currently running.
    """
    directory_exists = False
    try:
        mkdir(str(directory))
    except OSError as e:
        if e.errno == EEXIST:
            directory_exists = True
        else:
            raise e

    if not directory_exists:
        return False
        return False

    pid, create_time = _read_pid_file(pid_file)

    try:
        current = Process(pid)
    except NoSuchProcess:
        return False

    if current.create_time() == create_time:
        return True

    _delete(directory)
    return False


def _read_pid_file(filename):
    """Read the current process information from disk.
    :param filename: The name of the file containing the process information.
    :return: The PID and creation time of the current running process.
    """
    if not isfile(str(filename)):
        raise InvalidPidFileError()

    try:
        with open(filename, 'r') as f:
            pid, create_time = f.read().split()
        return int(pid), float(create_time)
    except ValueError:
        raise InvalidPidFileError()


def _set_running(directory):
    """Write the current process information to disk.
    :param directory: The name of the directory where the process information will be written.
    """
    if isfile(str(filename)):
        raise PidFileExistsError()

    p = Process()
    with open(filename, 'w') as f:
        f.write('{0} {1:.6f}'.format(p.pid, p.create_time()))


def _delete(directory):
    """Delete the process information directory on disk.
    :param directory: The name of the directory to be deleted.
    """
    try:
        rmtree(directory)
    except OSError:
        raise InvalidPidDirectoryError


def _get_pid_filename(directory):
    """Return the name of the process information file.
    :param directory: The name of the directory where the process information file
    is created.
    """
    return realpath(join(str(directory), 'INFO'))
