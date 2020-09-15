import connect
import os
import telnetlib


SSHHOST = '10.203.1.200'
SSHPORT = '22'
SSHUSER = 'root'
SSHPASSWORD = 'password'
TIMEOUT = 3

TELHOST = '10.203.1.231'
TELPORT = 23
TELUSER = 'root'
TELPASSWORD = 'Feixi@123'


class TestConnSSH:

    def setup_class(self):
        self.ssh = connect.ConnSSH(
            SSHHOST, SSHPORT, SSHUSER, SSHPASSWORD, TIMEOUT)

    def test_connect(self):
        assert self.ssh._connect() == None
        assert self.ssh.SSHConnection != None

    def test_execute_command(self):
        stsdir = self.ssh.execute_command('pwd')
        assert stsdir['sts'] == 1

    def test_make_connect(self):
        self.ssh.SSHConnection = None
        self.ssh._make_connect()
        assert self.ssh.SSHConnection != None

    def test_download(self):
        self.ssh.execute_command('echo \'this is test\' >> /pytest.txt')
        self.ssh.download('/pytest.txt', '/tmp/pytest.txt')
        file = os.popen('cat /tmp/pytest.txt')
        assert file.read() == 'this is test\n'
        self.ssh.execute_command('rm /pytest.txt')
        os.remove('/tmp/pytest.txt')

    def test_upload(self):
        os.system('echo \'this is test\' >> /tmp/pytest.txt')
        self.ssh.upload('/tmp/pytest.txt', '/pytest.txt')
        stsdir = self.ssh.execute_command('cat /pytest.txt')
        assert stsdir['rst'] == b'this is test\n'
        os.remove('/tmp/pytest.txt')
        self.ssh.execute_command('rm /pytest.txt')


class TestConnTelnet:

    def setup_class(self):
        self.telnet = connect.ConnTelnet(
            TELHOST, TELPORT, TELUSER, TELPASSWORD, TIMEOUT)

    def test_connect(self):
        self.telnet.telnet = telnetlib.Telnet()
        assert self.telnet._connect() == None

    def test_execute_command(self):
        assert self.telnet.execute_command('lun show') != None

    def test_make_connect(self):
        self.telnet.telnet = telnetlib.Telnet()
        assert self.telnet._make_connect() == None

