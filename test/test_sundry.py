import sundry
import consts
import connect
import os
import logdb
import storage
import vplx
import host_initiator as hi


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
    logdb.prepare_db()
    global VSSH
    VSSH = connect.ConnSSH(VPLX_IP, PORT, USER, PASSWORD, TIMEOUT)


def test_pick_iqns_random():
    consts.set_glo_iqn_list(['test_iqn1', 'test_iqn2'])
    assert sundry.pick_iqns_random(2) == ['test_iqn1', 'test_iqn2']


def test_generate_iqn():
    assert sundry.generate_iqn(
        100) == 'iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-100'


def test_generate_iqn_list():
    sundry.generate_iqn_list(2)
    assert consts.glo_iqn_list() == ['iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-0',
                                     'iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1']


def test_id_str_to_list():
    assert sundry.id_str_to_list('2') == [2]


def test_scsi_rescan():
    assert sundry.scsi_rescan(SSH, 'n') == True
    assert sundry.scsi_rescan(SSH, 'r') == True
    assert sundry.scsi_rescan(SSH, 'a') == True


# def test_get_lsscsi():
#     assert sundry.get_lsscsi(SSH, 'pytest', sundry.get_oprt_id())


def test_re_search():
    assert sundry.re_search('is', 'This is pytest')


def test_get_ssh_cmd():
    result = sundry.get_ssh_cmd(SSH, 'pytest', 'pwd', sundry.get_oprt_id())
    assert result['rst'] == b'/root\n'


def test_get_telnet_cmd():
    telnet = connect.ConnTelnet(NHOST, NPORT, NUSERNSME, NPASSWORD, TIMEOUT)
    assert '/vol/esxi/' in sundry.get_telnet_cmd(
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


# ##
# def test_pwe():
#     assert sundry.pwe('pytest', 2, 1) == None


# ##
# def test_pwce():
#     consts.set_glo_rpl('yes')
#     assert sundry.pwce('pytest', 2, 1) != None


# ##
# def test_handle_exception():
#     assert sundry.handle_exception() != None


def test_get_answer():
    consts.set_glo_rpl('yes')
    logger = consts.glo_log()
    logger.write_to_log('F', 'DATA', 'INPUT', 'pytest',
                        'confirm deletion', 'n')
    logdb.prepare_db()
    assert sundry.get_answer('yes') == 'n'
    consts.set_glo_rpl('no')


class TestGetNewDisk:

    def setup_class(self):
        self.stor = storage.Storage()
        self.stor.create_map()
        iqn1 = "iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1"
        consts.set_glo_iqn_list([iqn1])
        self.drbd = vplx.VplxDrbd()
        self.drbd.cfg()
        self.crm = vplx.VplxCrm()
        self.crm.cfg()
        hi.init_ssh()
        hi.change_iqn(iqn1)
        self.getdisk = sundry.GetNewDisk(SSH, VPLX_IP)

    def teardown_class(self):
        self.crm._del('res_pytest_99')
        self.drbd._del('res_pytest_99')
        self.stor.del_luns(['pytest_99'])

    def test_get_disk_from_netapp(self):
        getdisk = sundry.GetNewDisk(VSSH, NHOST)
        assert getdisk.get_disk_from_netapp() != None

    def test_get_disk_from_vplx(self):
        assert self.getdisk.get_disk_from_vplx() != None

    def test_find_new_disk(self):
        assert self.getdisk._find_new_disk('LIO-ORG') == '/dev/sdc'

    def test_get_disk_dev(self):
        assert self.getdisk._get_disk_dev('LIO-ORG') == '/dev/sdc'

    def test_get_lsscsi(self):
        assert self.getdisk._get_lsscsi(
            SSH, 'D37nG6Yi', sundry.get_oprt_id()) != None


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
        self.stor = storage.Storage()
        self.stor.create_map()
        self.iqn = "iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1"
        consts.set_glo_iqn_list([self.iqn])
        self.drbd = vplx.VplxDrbd()
        self.drbd.cfg()
        self.crm = vplx.VplxCrm()
        self.crm.cfg()
        self.iscsi = sundry.Iscsi(SSH, VPLX_IP)

    def teardown_class(self):
        self.crm._del('res_pytest_99')
        self.drbd._del('res_pytest_99')
        self.stor.del_luns(['pytest_99'])

    def test_create_session(self):
        self.iscsi._end_session(TARGET_IQN)
        assert self.iscsi.create_session() == True

    def test_end_session(self):
        self.iscsi.create_session()
        assert self.iscsi._end_session(TARGET_IQN) == True

    def test_logout(self):
        self.iscsi.create_session()
        assert self.iscsi._logout(TARGET_IQN) == True

    def test_login(self):
        self.iscsi._end_session(TARGET_IQN)
        assert self.iscsi.login() == True

    def test_find_session(self):
        assert self.iscsi._find_session() == True

    def test_modify_iqn(self):
        assert self.iscsi.modify_iqn(self.iqn) == None

    def test_restart_service(self):
        assert self.iscsi._restart_service() == True

    def test_modify_iqn_cfg_file(self):
        assert self.iscsi._modify_iqn_cfg_file(self.iqn) == True
