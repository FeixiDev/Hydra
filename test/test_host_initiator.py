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


def test_find_new_disk():
    assert hi._find_new_disk() == None


def test_get_disk_dev():
    assert hi.get_disk_dev() == None


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
        self.stor.lun_create()
        self.stor.lun_map()
        hi.init_ssh()
        s.scsi_rescan(hi.SSH, 'n')
        self.drbd = vplx.VplxDrbd()
        self.drbd.prepare_config_file()
        self.drbd.drbd_cfg()
        self.drbd.drbd_status_verify()
        s.generate_iqn(100)
        self.crm = vplx.VplxCrm()
        self.crm.crm_cfg()

    # def teardown_class(self):
    #     self.drbd.drbd_del(self.drbd.res_name)
    #     self.stor.lun_unmap('pytest_99')
    #     self.stor.lun_destroy('pytest_99')

    # def test_modify_host_iqn(self):
    #     assert self.host._modify_host_iqn() == True

    # def test_modify_iqn_and_restart(self):
    #     assert self.host.modify_iqn_and_restart() == True

    def test_prepare(self):
        assert self.host._prepare() == None

    def test_mount(self):
        dev = hi.get_disk_dev()
        assert self.host._mount(dev) == True

    def test_judge_format(self):
        assert self.host._judge_format() == True

    def test_format(self):
        assert self.host.format() == True

    def test_get_dd_perf(self):
        assert self.host._get_dd_perf() == True

    def test_get_test_perf(self):
        assert self.host.get_test_perf() == True

    def test_start_test(self):
        assert self.host.start_test() == True

    def test_host_rescan_r(self):
        assert self.host.host_rescan_r() == True
