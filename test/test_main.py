import subprocess
import time


def output(cmd):
    cmds = 'python3 main.py %s' % cmd
    output = subprocess.check_output(cmds, shell=True)
    return output.decode()


def test_help():
    out = output('')
    assert 'arguments' in out


def test_lun():
    out = output('lun -id 1 -s unittest')
    assert out != None
    out = output('lun -id 2 3 -s unittest')
    assert out != None


def test_iqn_o2n():
    # out = output('iqn o2n')
    pass


def test_iqn_n2n():
    out = output('iqn n2n -id 4 -c 2')
    assert out != None
    out = output('iqn n2n -id 5 6 -c 2')
    assert out != None


def test_iqn_n2n_n():
    out = output('iqn n2n -id 7 -c 2 -n 1')
    assert out != None
    out = output('iqn n2n -id 8 9 -c 2 -n 1')
    assert out != None


def test_del():
    cmd = 'python3 main.py del'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data, stderr_data = p.communicate()
    assert stdout_data != None


def test_del_s():
    output('lun -id 1 -s unittest')
    cmd = 'python3 main.py del -s unittest'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data, stderr_data = p.communicate()
    assert stdout_data != None


def test_del_id():
    output('lun -id 2 -s unittest')
    cmd = 'python3 main.py del -id 2'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data, stderr_data = p.communicate()
    assert stdout_data != None


def test_del_s_id():
    output('lun -id 2 -s unittest')
    cmd = 'python3 main.py del -s unittest -id 2'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data, stderr_data = p.communicate()
    assert stdout_data != None


def test_rpl_a():
    out = output('rpl -a')
    assert out != None


def test_rpl_t():
    log = r'''[2020/09/16 15:04:00] [1600239840] [T] [DATA] [input] [user_input] [] [{'valid': '1', 'cmd': 'lun -id 1 -s unittest'}]|
[2020/09/16 15:04:00] [1600239840] [T] [INFO] [info] [start] [8100624309] [Start to connect 10.203.1.231 via Telnet]|
[2020/09/16 15:04:00] [1600239840] [F] [DATA] [value] [dict] [data for telnet connect] [{'host': '10.203.1.231', 'port': 23, 'username': 'root', 'password': 'Feixi@123'}]|
[2020/09/16 15:04:01] [1600239840] [T] [INFO] [info] [start] [2063149801] [Start to connect 10.203.1.199 via SSH]|
[2020/09/16 15:04:01] [1600239840] [F] [DATA] [value] [dict] [data for SSH connect] [{'host': '10.203.1.199', 'port': 22, 'username': 'root', 'password': 'password'}]|
[2020/09/16 15:04:01] [1600239840] [T] [INFO] [info] [start] [9231610804] [Start to connect 10.203.1.200 via SSH]|
[2020/09/16 15:04:01] [1600239840] [F] [DATA] [value] [dict] [data for SSH connect] [{'host': '10.203.1.200', 'port': 22, 'username': 'root', 'password': 'password'}]|
[2020/09/16 15:04:03] [1600239840] [T] [INFO] [info] [start] [] [Start to modify IQN on Host]|
[2020/09/16 15:04:03] [1600239840] [T] [INFO] [info] [start] [] [Check up the status of session]|
[2020/09/16 15:04:03] [1600239840] [F] [DATA] [STR] [V9jGOP1i] [] [9162083304]|
[2020/09/16 15:04:03] [1600239840] [T] [OPRT] [cmd] [ssh] [9162083304] [iscsiadm -m session]|'''
    with open('Hydra_log.log', 'a') as file:  
        file.write(log)  
    out = output('rpl -t 1600239840')
    assert out != None


def test_rpl_d():
    out = output('rpl -d \'2020/09/16 15:04:00\' \'2020/09/16 16:00:00\'')
    assert out != None
