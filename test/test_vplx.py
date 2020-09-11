import vplx
import sundry as s
import log
import consts
import storage
import logdb
import os
import pytest


def setup_module():
    vplx.init_ssh()


def test_init_ssh():
    assert vplx.SSH != None


def test_rescan_after_remove():
    assert vplx.rescan_after_remove() == None


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
        self.stor = storage.Storage()
        self.stor.create_map()
        s.scsi_rescan(vplx.SSH, 'n')
        self.drbd = vplx.VplxDrbd()

    def teardown_class(self):
        self.stor.del_luns(['pytest_99'])

    def test_prepare(self):
        self.drbd._prepare()
        assert vplx.SSH != None

    def test_cfg(self):
        assert self.drbd.cfg() == None
        self.drbd._del('res_pytest_99')

    def test_add_config_file(self):
        assert self.drbd._add_config_file('res_pytest_99') == None
        self.drbd._del_config('res_pytest_99')

    def test_create_config_file(self):
        netapp = '10.203.1.231'
        blk_dev_name = s.GetNewDisk(vplx.SSH, netapp).get_disk_from_netapp()
        assert self.drbd._create_config_file(blk_dev_name, 'res_pytest_99') == None
        self.drbd._del_config('res_pytest_99')

    #cfg 全局变量 无法传递
    def test_init(self):
        self.drbd._add_config_file('res_pytest_99')
        assert self.drbd._init('res_pytest_99') == True
        self.drbd._del_config('res_pytest_99')

    def test_up(self):
        self.drbd._add_config_file('res_pytest_99')
        self.drbd._init('res_pytest_99')
        assert self.drbd._up('res_pytest_99') == True
        self.drbd._del('res_pytest_99')

    def test_primary(self):
        self.drbd._add_config_file('res_pytest_99')
        self.drbd._init('res_pytest_99')
        self.drbd._up('res_pytest_99')
        assert self.drbd._primary('res_pytest_99') == True
        self.drbd._del('res_pytest_99')

    def test_status_verify(self):
        self.drbd._add_config_file('res_pytest_99')
        self.drbd._init('res_pytest_99')
        self.drbd._up('res_pytest_99')
        self.drbd._primary('res_pytest_99')
        assert self.drbd.status_verify('res_pytest_99') == True
        self.drbd._del('res_pytest_99')

    def test_down(self):
        self.drbd.cfg()
        assert self.drbd._down('res_pytest_99') == True
        self.drbd._del_config('res_pytest_99')

    def test_del_config(self):
        self.drbd._add_config_file('res_pytest_99')
        assert self.drbd._del_config('res_pytest_99') == True

    def test_get_all_cfgd_drbd(self):
        assert self.drbd.get_all_cfgd_drbd()

    def test_del(self):
        self.drbd.cfg()
        assert self.drbd._del('res_pytest_99') == True

    def test_del_drbds(self):
        self.drbd.cfg()
        assert self.drbd.del_drbds(['res_pytest_99']) == None


class TestVplxCrm:

    def setup_class(self):
        self.crm = vplx.VplxCrm()
        self.stor = storage.Storage()
        self.stor.id = '99'
        self.stor.str = 'pytest'
        self.stor.create_map()
        s.scsi_rescan(vplx.SSH, 'n')
        self.drbd = vplx.VplxDrbd()
        self.drbd.cfg()
        s.generate_iqn(100)

    def teardown_class(self):
        self.drbd._del('res_pytest_99')
        self.stor._unmap_lun('pytest_99')
        self.stor._destroy_lun('pytest_99')

    def test_cfg(self):
        assert self.crm.cfg() == True

    def test_modify_initiator_and_verify(self):
        assert self.crm.modify_initiator_and_verify() == None

    def test_create(self):
        assert self.crm._create() == True

    def test_set_col(self):
        assert self.crm._setting_col() == True

    def test_set_order(self):
        assert self.crm._setting_order() == True

    def test_set_portblock(self):
        assert self.crm._set_portblock() == True

    def test_setting(self):
        assert self.crm._setting() == True

    def test_start(self):
        assert self.crm._crm_start() == True

    def test_status_verify(self):
        assert self.crm._status_verifz() == True

    def test_get_crm_status(self):
        assert self.crm._get_crm_status() == True

    def test_cyclic_check_crm_status(self):
        assert self.crm._cyclic_check_crm_status() == True

    def test_stop(self):
        assert self.crm._stop() == True

    def test_del_cof(self):
        assert self.crm._del_cof() == True

    def test_del(self):
        assert self.crm._del() == True

    def test_get_all_cfgd_res(self):
        assert self.crm.get_all_cfgd_res()

    def test_del_crms(self):
        assert self.crm.del_crms() == None

    def test_vplx_rescan_r(self):
        assert self.crm.vplx_rescan_r() == None

    def test_modify_allow_initiator(self):
        assert self.crm._modify_allow_initiator() == True

    def test_targetcli_verify(self):
        assert self.crm._targetcli_verify() == True

    def test_cyclic_check_crm_start(self):
        assert self.crm._cyclic_check_crm_start() == True

    def test_crm_and_targetcli_verify(self):
        assert self.crm._crm_and_targetcli_verify() == None
