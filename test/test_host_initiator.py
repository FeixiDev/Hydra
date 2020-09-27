import host_initiator as hi
import consts
import os
import subprocess
import vplx
import storage
import sundry as s


def test_init_ssh():
    hi.init_ssh()
    assert hi.SSH != None


def test_umount_mnt():
    assert hi.umount_mnt() == None


def test_change_iqn():
    hi.init_ssh()
    iqn = "iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1"
    assert hi.change_iqn(iqn) == None


def test_rescan_after_remove():
    assert hi.rescan_after_remove() == None


class TestDebugLog:

    def setup_class(self):
        self.debuglog = hi.DebugLog()
        tid = consts.glo_tsc_id()
        self.debug_folder = f'/tmp/{tid}/'
        os.mkdir(self.debug_folder)

    def test_collect_debug_sys(self):
        assert self.debuglog.collect_debug_sys() == None

    def test_get_all_log(self):
        self.debuglog.get_all_log(self.debug_folder)
        assert '10.203.1.200.tar' in os.listdir(self.debug_folder)


class TestHostTest:

    def setup_class(self):
        self.host = hi.HostTest()
        self.stor = storage.Storage()
        self.stor.create_map()
        iqn1 = "iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1"
        consts.set_glo_iqn_list([iqn1])
        self.drbd = vplx.VplxDrbd()
        self.drbd.cfg()
        self.crm = vplx.VplxCrm()
        self.crm.cfg()
        hi.init_ssh()
        iqn = "iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:99-1"
        hi.change_iqn(iqn)
        VPLX_IP = '10.203.1.199'
        gnd = s.GetNewDisk(hi.SSH, VPLX_IP)
        self.dev_name = gnd.get_disk_from_vplx()

    def teardown_class(self):
        self.crm._del('res_pytest_99')
        self.drbd._del('res_pytest_99')
        self.stor.del_luns(['pytest_99'])

    def test_prepare(self):
        assert self.host._prepare() == None

    def test_mount(self):
        self.host._format(self.dev_name)
        assert self.host._mount(self.dev_name)
        hi.umount_mnt()

    def test_judge_format(self):
        string = 'done done done done'
        assert self.host._judge_format(string) == True

    def test_format(self):
        assert self.host._format(self.dev_name) == True

    def test_mount_disk(self):
        assert self.host._mount_disk() == True

    def test_get_test_perf(self):
        mount_point = '/mnt'
        cmd_dd_write = f'dd if=/dev/zero of={mount_point}/t.dat bs=512k count=16'
        assert self.host._get_test_perf(cmd_dd_write, unique_str='CwS9LYk0')

    def test_write_test(self):
        assert self.host._write_test() == None

    def test_read_test(self):
        assert self.host._read_test() == None
        hi.umount_mnt()

    def test_io_test(self):
        assert self.host.io_test() == None
        hi.umount_mnt()
