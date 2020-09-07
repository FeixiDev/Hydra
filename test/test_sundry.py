import sundry
import consts
import connect
import os


VPLX_IP = '10.203.1.199'
HOST = '10.203.1.200'
PORT = 22
USER = 'root'
PASSWORD = 'password'
TIMEOUT = 3
TARGET_IQN = 'iqn.2020-06.com.example:test-max-lun'
NHOST = '10.203.1.231'
NPORT = 23
NUSERNSME = 'root'
NPASSWORD = 'Feixi@123'


def setup_module():
    global SSH
    SSH = connect.ConnSSH(HOST, PORT, USER, PASSWORD, TIMEOUT)


def test_host_random_iqn():
    consts.set_glo_iqn_list(['test_iqn1', 'test_iqn2'])
    assert sundry.host_random_iqn(2) == ['test_iqn1', 'test_iqn2']


def test_generate_iqn():
    assert sundry.generate_iqn(
        100) == 'iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-100'


def test_generate_iqn_list():
    sundry.generate_iqn_list(2)
    assert consts.glo_iqn_list() == ['iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-0',
                                     'iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1']


def test_change_id_range_to_list():
    assert sundry.change_id_range_to_list('2') == [2]


def test_scsi_rescan():
    assert sundry.scsi_rescan(SSH, 'n') == True
    assert sundry.scsi_rescan(SSH, 'r') == True
    assert sundry.scsi_rescan(SSH, 'a') == True


def test_get_lsscsi():
    assert sundry.get_lsscsi(SSH, 'pytest', sundry.get_oprt_id())


def test_re_search():
    assert sundry.re_search('is', 'This is pytest')


def test_get_ssh_cmd():
    result = sundry.get_ssh_cmd(SSH, 'pytest', 'pwd', sundry.get_oprt_id())
    assert result['rst'] == b'/root\n'


def test_ex_telnet_cmd():
    telnet = connect.ConnTelnet(NHOST, NPORT, NUSERNSME, NPASSWORD, TIMEOUT)
    assert '/vol/esxi/' in sundry.ex_telnet_cmd(
        telnet, 'pytest', 'lun show', 'pytest')


def test_compare():
    assert sundry._compare('disk', ['disk', 'pytest']) == 'disk'
    assert sundry._compare('disk', ['res_disk', 'res_pytest']) == 'res_disk'


def test_get_to_del_list():
    assert sundry.get_to_del_list(['disk', 'pytest']) == ['pytest']


def test_prt_res_to_del():
    assert sundry.prt_res_to_del('pytest', ['res_disk', 'res_pytest']) == None


def test_get_transaction_id():
    tid = sundry.get_transaction_id()
    assert isinstance(tid, str)


def test_get_oprt_id():
    assert sundry.get_oprt_id()


def test_change_pointer():
    sundry.change_pointer(100)
    assert consts.glo_log_id() == 100


def test_re_findall():
    assert sundry.re_findall('t', 'pytest') == ['t', 't']


def test_ran_str():
    assert sundry.ran_str(3)


def test_prt():
    assert sundry.prt('pytest') == None


def test_pwl():
    assert sundry.pwl('pytest', 3) == None


def test_prt_log():
    assert sundry.prt_log('pytest', 3, 3) == None


def test_pwe():
    assert sundry.pwe('pytest', 3, 1) == None


def test_pwce():
    assert sundry.pwce('pytest', 3, 1) == None


def test_handle_exception():
    assert sundry.handle_exception() == None


class TestGetNewDisk:

    def setup_class(self):
        consts.set_glo_id(0)
        self.getdisk = sundry.GetNewDisk(SSH, NHOST)

    ##
    def test_get_disk_from_netapp(self):
        assert self.getdisk.get_disk_from_netapp() == None

    def test_get_disk_from_vplx(self):
        assert self.getdisk.get_disk_from_vplx() == None

    def test_find_new_disk(self):
        assert self.getdisk.find_new_disk('VMware') == '/dev/sda'

    def test_get_disk_dev(self):
        assert self.getdisk.get_disk_dev('VMware') == '/dev/sda'


class TestDebugLog:

    def setup_class(self):
        tid = consts.glo_tsc_id()
        self.debug_folder = f'/var/log/{tid}'
        local_debug_folder = f'/tmp/{tid}/'
        os.mkdir(local_debug_folder)
        self.local_file = f'/tmp/{tid}/{HOST}.tar'
        self.debug = sundry.DebugLog(SSH, self.debug_folder, HOST)

    def test_mk_debug_folder(self):
        self.debug.SSH.execute_command(f'rm -rf {self.debug_folder}')
        assert self.debug._mk_debug_folder() == None

    def test_prepare_debug_log(self):
        assert self.debug.prepare_debug_log(['pwd']) == None

    def test_get_debug_log(self):
        assert self.debug.get_debug_log(self.local_file) == None


class TestIscsi:

    def setup_class(self):
        self.iscsi = sundry.Iscsi(SSH, VPLX_IP)
        self.iqn = 'iqn.2020-06.com.example:test-max-host'

    def test_create_session(self):
        assert self.iscsi.create_session() == None

    def test_disconnect_session(self):
        assert self.iscsi.disconnect_session(self.iqn) == True

    def test_logout(self):
        assert self.iscsi._logout(self.iqn) == True

    def test_login(self):
        assert self.iscsi.login() == True

    def test_find_session(self):
        assert self.iscsi._find_session() == True

    def test_restart_service(self):
        assert self.iscsi.restart_service() == True

    def test_modify_host_iqn(self):
        assert self.iscsi.modify_host_iqn(self.iqn) == True
