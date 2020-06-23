#  coding: utf-8
import paramiko
import time
import telnetlib
import sys
import sundry as s
import pprint
import traceback


class ConnSSH(object):
    '''
    ssh connect to VersaPLX
    '''

    def __init__(self, host, port, username, password, timeout,logger):
        self.logger = logger
        self._host = host
        self._port = port
        self._timeout = timeout
        self._username = username
        self._password = password
        self.SSHConnection = None
        self._connect()

    def _connect(self):
        try:
            objSSHClient = paramiko.SSHClient()
            objSSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.logger.write_to_log('SSH','SSH_connect','',[self._host,self._port,self._username,self._password,self._timeout])
            # log : SSH_connect [host,port,username,password,timeout]
            objSSHClient.connect(self._host, port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 timeout=self._timeout)
            # 如何验证SSH连接成功
            # log : SSH_connect_result [T/F]
            self.logger.write_to_log('SSH','SSH_connect','','SSH SUCCESS')
            self.SSHConnection = objSSHClient
        except Exception as e:
            # log : Error [(print)]
            self.logger.write_to_log('SSH', 'ssh_connect_error', '', (str(traceback.format_exc())))
            self.logger.write_to_log('SSH','print','',(f'Connect to {self._host} failed with error: {e}'))
            s.pe(f'Connect to {self._host} failed with error: {e}')

    def excute_command(self, command):
        self.logger.write_to_log('SSH','ssh_ex_cmd','',command)
        stdin, stdout, stderr = self.SSHConnection.exec_command(command) # ？
        data = stdout.read()
        self.logger.write_to_log('SSH','ssh_ex_cmd_result_stdout',command,data)
        if len(data) > 0:
            self.logger.write_to_log('SSH','ssh_ex_cmd_return',command,data)
            return data

        err = stderr.read()
        self.logger.write_to_log('SSH','ssh_ex_cmd_result_stderr',command,err)
        if len(err) > 0:
            print(err.strip())
            self.logger.write_to_log('SSH','print','',(err.strip()))
            self.logger.write_to_log('SSH','ssh_ex_cmd_return',command,err)
            return err

        if data == b'':
            self.logger.write_to_log('SSH', 'ssh_ex_cmd_return', command, True)
            return True

    def close(self):
        self.logger.write_to_log('SSH','ssh_close','','start')
        self.SSHConnection.close()
        self.logger.write_to_log('SSH', 'ssh_close', '', 'end')


class ConnTelnet(object):
    '''
    telnet connect to NetApp 
    '''

    def __init__(self, host, port, username, password, timeout,logger):
        self.logger = logger
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._timeout = timeout
        self.telnet = telnetlib.Telnet()
        self._connect()

    def _connect(self):
        try:
            # log : telnet_open
            self.telnet.open(self._host, self._port)
            self.logger.write_to_log('Telnet', 'telnet_open', 'ip:%s,port:%s' % (self._host, self._port), '')
            # log: telnet_open_result 这个有没有结果的
            # log : username
            date_read1 =  self.telnet.read_until(b'Username:', timeout=1)
            self.logger.write_to_log('Telnet','telnet_read_until','Username/timeout=1',date_read1)
            self.logger.write_to_log('Telnet','telnet_write','',self._username.encode() + b'\n')
            self.telnet.write(self._username.encode() + b'\n')
            # 写入之后的结果怎么判断，

            date_read2 = self.telnet.read_until(b'Password:', timeout=1)
            self.logger.write_to_log('Telnet','telnet_read_until','Password/timeout=1',date_read2)
            self.logger.write_to_log('Telnet','telnet_write','',self._password.encode() + b'\n')
            self.telnet.write(self._password.encode() + b'\n')

        except Exception as e:
            self.logger.write_to_log('Telnet', 'telnet_connect_error', '', (str(traceback.format_exc())))
            self.logger.write_to_log('Telnet','print','',(f'Connect to {self._host} failed with error: {e}'))
            s.pe(f'Connect to {self._host} failed with error: {e}')

    # 定义exctCMD函数,用于执行命令
    def excute_command(self, cmd):
        # log: NetApp_ex_cmd
        self.logger.write_to_log('Telnet','telnet_ex_cmd','',cmd.encode().strip() + b'\r')
        self.telnet.write(cmd.encode().strip() + b'\r')
        # 命令的结果的记录？
        self.logger.write_to_log('Telnet','telnet_ex_cmd','','time_sleep:0.25')
        time.sleep(0.25)
        rely = self.telnet.read_very_eager().decode()# ?

    def close(self):
        self.logger.write_to_log('Telnet','Telnet_close','','start')
        self.telnet.close()
        self.logger.write_to_log('Telnet', 'Telnet_close', '', 'end')

if __name__ == '__main__':
# telnet
    host='10.203.1.231'
    port='22'
    username='root'
    password='Feixi@123'
    timeout=5
    ssh=ConnSSH(host, port, username, password, timeout)
    strout=ssh.excute_command('?')
    w = strout.decode('utf-8')
    print(type(w))
    print(w.split('\n'))
    pprint.pprint(w)
    time.sleep(2)
    strout=ssh.excute_command('lun show -m')
    pprint.pprint(strout)


    # telnet
    # host='10.203.1.231'
    # Port='23'
    # username='root'
    # password='Feixi@123'
    # timeout=10

    pass
