import sys
import paramiko
import traceback


def filetransfer(func):
    def wrapper(self, *args):
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        try:
            func(self, *args)
        except:
            traceback.print_exc()
        sftp.close()
    return wrapper


class CommandIssue:

    """
    paramiko传送指令到远程服务器
    """

    def __init__(self, ip):
        self.ip = ip
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        """连接"""
        self.ssh.connect(hostname=self.ip, port=22, username="root", password="Abc123456789!")

    def close(self):
        """断开"""
        self.ssh.close()

    def execute(self, cmds):
        """执行指令"""
        stdin, stdout, stderr = self.ssh.exec_command(cmds)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
#         _stdout = "         ".join(stdout) if stdout else ""
#         _stderr = "         ".join(stderr) if stderr else ""
#         sys.stdout.write("""
# ---------------------------------
# commands: {}
#   stdout: {}
#   stderr: {}
# """.format(cmds, _stdout, _stderr))
        return stdout

    @filetransfer
    def put(self, source, target):
        sftp.put(source, target)

    @filetransfer
    def get(self, source, target):
        sftp.get(source, target)