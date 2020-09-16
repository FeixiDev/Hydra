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
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data,stderr_data = p.communicate()
    assert stdout_data != None


def test_del_s():
    output('lun -id 1 -s unittest')
    cmd = 'python3 main.py del -s unittest'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data,stderr_data = p.communicate()
    assert stdout_data != None


def test_del_id():
    output('lun -id 2 -s unittest')
    cmd = 'python3 main.py del -id 2'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data,stderr_data = p.communicate()
    assert stdout_data != None


def test_del_s_id():
    output('lun -id 2 -s unittest')
    cmd = 'python3 main.py del -s unittest -id 2'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    time.sleep(3)
    p.stdin.write(b'y')
    stdout_data,stderr_data = p.communicate()
    assert stdout_data != None

