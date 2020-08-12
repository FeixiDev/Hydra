import vplx
import sundry as s
import log
import consts
import storage
import logdb
import os
import pytest


vplx.init_ssh()


def test_init_ssh():
    assert vplx.SSH != None


def test_find_new_disk():
    Storage = storage.Storage()
    Storage.lun_create()
    Storage.lun_map()
    s.scsi_rescan(vplx.SSH, 'n')
    assert '/dev/' in vplx._find_new_disk()
    Storage.lun_unmap('pytest_99')
    Storage.lun_destroy('pytest_99')


def test_get_disk_dev():
    assert '/dev/' in vplx.get_disk_dev()


class TestDebugLog:

    def setup_class(self):
        self.debuglog = vplx.DebugLog()

    def test_collect_debug_sys(self):
        assert self.debuglog.collect_debug_sys() == None

    def test_collect_debug_drbd(self):
        assert self.debuglog.collect_debug_drbd() == None

    def test_collect_debug_crm(self):
        assert self.debuglog.collect_debug_crm() == None

    def test_get_all_log(self):
        tid = consts.glo_tsc_id()
        local_debug_folder = f'/tmp/{tid}/'
        os.mkdir(local_debug_folder)
        assert self.debuglog.get_all_log(local_debug_folder) == None


class TestVplxDrbd:

    def setup_class(self):
        self.drbd = vplx.VplxDrbd()
        logdb.prepare_db()
        self.Storage = storage.Storage()
        self.Storage.lun_create()
        self.Storage.lun_map()
        s.scsi_rescan(vplx.SSH, 'n')

    def teardown_class(self):
        self.Storage.lun_unmap('pytest_99')
        self.Storage.lun_destroy('pytest_99')

    def test_prepare(self):
        self.drbd._prepare()
        assert vplx.SSH != None

    def test_prepare_config_file(self):
        assert self.drbd.prepare_config_file() == None

    def test_drbd_init(self):
        assert self.drbd._drbd_init() == True

    def test_drbd_up(self):
        assert self.drbd._drbd_up() == True

    def test_drbd_primary(self):
        assert self.drbd._drbd_primary() == True

    def test_drbd_status_verify(self):
        assert self.drbd.drbd_status_verify() == True

    def test_get_all_cfgd_drbd(self):
        assert self.drbd.get_all_cfgd_drbd()

    def test_drbd_down(self):
        assert self.drbd._drbd_down(self.drbd.res_name) == True

    def test_drbd_del_config(self):
        assert self.drbd._drbd_del_config(self.drbd.res_name) == True

    # def test_drbd_cfg(self):
    #     self.drbd.prepare_config_file()
    #     assert self.drbd.drbd_cfg() == True

    # def test_drbd_del(self):
    #     assert self.drbd.drbd_del(self.drbd.res_name) == True

    # def test_del_all(self):
    #     assert self.drbd.del_all() == True


class TestVplxCrm:
    
    def setup_class(self):
        self.crm = vplx.VplxCrm()
        self.Storage = storage.Storage()
        self.Storage.lun_create()
        self.Storage.lun_map()
        s.scsi_rescan(vplx.SSH, 'n')
        self.drbd = vplx.VplxDrbd()
        self.drbd.prepare_config_file()
        self.drbd.drbd_cfg()
        s.generate_iqn(100)

    def teardown_class(self):
        self.drbd.drbd_del(self.drbd.res_name)
        self.Storage.lun_unmap('pytest_99')
        self.Storage.lun_destroy('pytest_99')

    def test_crm_create(self):
        assert self.crm._crm_create() == True

    def test_setting_col(self):
        assert self.crm._setting_col() == True

    def test_setting_order(self):
        assert self.crm._setting_order() == True

    def test_crm_start(self):
        assert self.crm._crm_start() == True

    def test_crm_stop(self):
        assert self.crm._crm_stop(self.drbd.res_name) == True

    def test_crm_del(self):
        assert self.crm._crm_del(self.drbd.res_name) == True
        