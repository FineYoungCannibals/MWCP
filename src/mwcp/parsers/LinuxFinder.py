import re
import logging
from mwcp import Parser, metadata
import pdb
import subprocess
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SSHPublicKey(Parser):
    DESCRIPTION = "SSHPublicKey Parser"
    AUTHOR = "fh"

    @classmethod
    def identify(cls, file_object):
        return True

    def run(self):
        regex=r'((?:ssh|ecdsa)[^\s]+)\s+([^\s]+)(?:\s+([^\n]+))?\n'
        logger.info(f"{self.DESCRIPTION} by {self.AUTHOR}")
        file_content = self.file_object.data.decode(errors="backslashreplace")
        matches = re.findall(regex, file_content, re.IGNORECASE)
        for m in matches:
            self.report.add(metadata.Other('ssh_public_key',m[1]))
            self.report.add(metadata.Other('ssh_public_key_type',m[0]))
            self.report.add(metadata.Other('ssh_public_key_user',m[2]))


class SSHPrivateKey(Parser):
    DESCRIPTION = "SSH Private Key Parser"
    AUTHOR = "fh"    

    @classmethod
    def identify(cls, file_object):
        return True

    def isencrypted(self,data):
        tmp_file = open('/tmp/temp.file','w')
        tmp_file.write(data)
        tmp_file.flush()
        tmp_file.close()
        os.chmod('/tmp/temp.file',0o600)

        result = subprocess.run(['ssh-keygen','-f','/tmp/temp.file', '-y','-P', ''],
            capture_output=True, text=True
        )
        if len(result.stdout) > 0:
            return False,result.stdout
        else:
            return True,""

    def run(self):
        regex=r'(\-{5}BEGIN\x20[^\x20]+\x20PRIVATE\x20KEY\-{5}\n.*?\-{5}END\x20[^\x20]+\x20PRIVATE\x20KEY\-{5})'
        logger.info(f"{self.DESCRIPTION} by {self.AUTHOR}")
        file_content = self.file_object.data.decode(errors="backslashreplace")
        matches = re.findall(regex, file_content, re.DOTALL)
        test_is_encrypted = self.isencrypted(file_content)
        for m in matches:
            if test_is_encrypted[0]:
                self.report.add(metadata.Other("Encrypted_SSH_Private_Key",m))
            else:
                self.report.add(metadata.Other("Unencrypted_SSH_Private_Key",m))
                self.report.add(metadata.Other("Associated_Public_Key",test_is_encrypted[1]))

class KnownHosts(Parser):
    DESCRIPTION = "known hosts file parser for ssh hunting"
    AUTHOR = "fh"
    @classmethod
    def identify(cls, file_object):
        data = file_object.data.decode(errors="backslashreplace")
        if len(re.findall('\|1\|',data,re.DOTALL))>1:
            return True
        else:
            return False
    def run(self):
        regex = r'\|\d\|(?P<ip>.*?)\|(?P<hostname>.*?)\s+(?P<key>.*?)[\n$]'
        logger.info(f"{self.DESCRIPTION} by {self.AUTHOR}")
        file_content = self.file_object.data.decode(errors="backslashreplace")
        matches = re.findall(regex, file_content, re.IGNORECASE)
        for m in matches:
            self.report.add(metadata.Other('unsalted_ip_hash',m[0]))
            self.report.add(metadata.Other('unsalted_hostname_hash',m[1]))
            self.report.add(metadata.Other('ssh_server_fingerprint',m[2]))

class Viminfo(Parser):
    DESCRIPTION = "VIM Info Parser"
    AUTHOR = "fh"

    @classmethod
    def identify(cls, file_object):
        return True

    def run(self):
        logger.info(f"{self.DESCRIPTION} by {self.AUTHOR}")
        file_content = self.file_object.data.decode(errors="backslashreplace")

        logger.info(f"Commands Parsing")
        commands_result= []
        cli_history_regex = r'\# Command Line History \(newest to oldest\)\:\n(.*?)\n\n'
        command_matches = re.findall(cli_history_regex, file_content, re.DOTALL)
        if len(command_matches) > 0:
            for command in command_matches:
                commands_result.extend([x for x in command.split('\n') if not x.startswith("|")])
                self.report.add(metadata.Other('command_history',str(commands_result)))

        logger.info(f"Search Parsing")
        search_result= []
        search_regex=r'\# Search String History \(newest to oldest\)\:\n(?:(.*?)\n\|[^\n]+)*?\n\n'
        search_matches = re.findall(search_regex, file_content, re.DOTALL)
        if len(search_matches) > 0:
            for search in search_matches:
                logger.info(f"{search}")
                search_result.extend([x for x in search.split('\n') if not x.startswith("|")])
                self.report.add(metadata.Other('search_history',str(search_result)))

        logger.info(f"File History Parsing")
        file_result= []
        file_history_regex = r'\# (?:Jumplist|Registers|File marks)[^\:]*?\:\n(.*?)\n\n'
        file_history_matches = re.findall(file_history_regex, file_content, re.DOTALL)
        if len(file_history_matches) > 0:
            for handle in file_history_matches:
                file_result.extend([x for x in handle.split('\n') if not x.startswith("|")])
                self.report.add(metadata.Other('file_history',str(file_result)))
