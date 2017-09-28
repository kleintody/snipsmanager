# -*-: coding utf-8 -*-

import os

from ..base import Base
from ...utils.os_helpers import file_exists
from ...utils.snipsfile import Snipsfile
from ...utils.os_helpers import is_raspi_os

from ..assistant.fetch import AssistantFetcher
from ..assistant.load import AssistantLoader
from ..setup.microphone import MicrophoneInstaller
from ..setup.systemd.bluetooth import SystemdBluetooth
from ..setup.systemd.snips import SystemdSnips
from ..setup.systemd.snipsskills import SystemdSnipsSkills
from .skills import SkillsInstaller, SkillsInstallerWarning
from .bluetooth import BluetoothInstaller

from ... import DEFAULT_SNIPSFILE_PATH

from snipsskillscore import pretty_printer as pp

class GlobalInstallerException(Exception):
    pass

class GlobalInstallerWarning(Exception):
    pass


class GlobalInstaller(Base):
    
    def run(self):
        try:
            GlobalInstaller.install(self.options['--snipsfile'], skip_bluetooth=self.options['--skip_bluetooth'], skip_systemd=self.options['--skip_systemd'])
        except GlobalInstallerWarning as e:
            pp.pwarning(str(e))
        except Exception as e:
            pp.perror(str(e))


    @staticmethod
    def install(snipsfile_path=None, skip_bluetooth=False, skip_systemd=False):
        snipsfile_path = snipsfile_path or DEFAULT_SNIPSFILE_PATH
        if snipsfile_path is not None and not file_exists(snipsfile_path):
            raise SkillsInstallerException("Error installing skills: Snipsfile not found.")
        snipsfile = Snipsfile(snipsfile_path)
        GlobalInstaller.install_from_snipsfile(snipsfile)


    @staticmethod
    def install_from_snipsfile(snipsfile, skip_bluetooth=False, skip_systemd=False):
        pp.pheader("Running Snips Skills installer")

        if snipsfile is None:
            raise SkillsInstallerException("Error running installer: no Snipsfile provided.")

        if is_raspi_os():
            try:
                AssistantFetcher.fetch()
                AssistantLoader.load()
            except Exception as e:
                pp.pwarning(str(e))
        else:
            pp.pwarning("Skipping assistant installation (Raspberry Pi only).")

        try:
            SkillsInstaller.install()
        except Exception as e:
            pp.pwarning(str(e))
        
        try:
            MicrophoneInstaller.install()
        except Exception as e:
            pp.pwarning(str(e))

        if not skip_bluetooth and is_raspi_os():
            try:
                BluetoothInstaller.install()
            except Exception as e:
                pp.pwarning(str(e))

        if not skip_systemd and is_raspi_os():
            try:
                SystemdBluetooth.setup()
            except Exception as e:
                pp.pwarning(str(e))
            try:
                SystemdSnips.setup()
            except Exception as e:
                pp.pwarning(str(e))
            try:
                SystemdSnipsSkills.setup()
            except Exception as e:
                pp.pwarning(str(e))