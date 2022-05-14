import argparse
import logging
import os.path as osp

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from DesktopApp import __appname__
from DesktopApp import __version__
from DesktopApp.app import MainWindow
from DesktopApp.logger import logger
from DesktopApp.qutils import newIcon


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version', '-V', action='store_true', help='show version'
    )
    parser.add_argument(
        '--reset-config', action='store_true', help='reset qt config'
    )
    parser.add_argument(
        '--logger-level',
        default='info',
        choices=['debug', 'info', 'warning', 'fatal', 'error'],
        help='logger level',
    )
    args = parser.parse_args()

    if args.version:
        print('{0} {1}'.format(__appname__, __version__))
        sys.exit(0)

    logger.setLevel(getattr(logging, args.logger_level.upper()))

    config_from_args = args.__dict__
    config_from_args.pop('version')
    reset_config = config_from_args.pop('reset_config')

    translator = QtCore.QTranslator()
    translator.load(
        QtCore.QLocale.system().name(),
        osp.dirname(osp.abspath(__file__)) + '/translate'
    )
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon('icon'))
    app.installTranslator(translator)
    win = MainWindow()

    if reset_config:
        logger.info('Resetting Qt config: %s' % win.settings.fileName())
        win.settings.clear()
        sys.exit(0)

    win.show()
    win.raise_()
    sys.exit(app.exec_())


# this main block is required to generate executable by pyinstaller
if __name__ == '__main__':
    main()
