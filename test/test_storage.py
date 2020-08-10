import storage
import consts
import sundry as s
import os


def test_init_telnet():
    storage.init_telnet()
    assert storage.TELNET_CONN != None


class TestDebugLog:

    def setup_class(self):
        self.debuglog = storage.DebugLog()

    def test_get_storage_debug(self):
        tid = consts.glo_tsc_id()
        local_debug_folder = f'/tmp/{tid}/'
        os.mkdir(local_debug_folder)
        assert self.debuglog.get_storage_debug(local_debug_folder) == None


class TestStorage:

    def setup_class(self):
        storage.init_telnet()
        self.storage = storage.Storage()
        self.oprt_id = s.get_oprt_id()

    def test_ex_telnet_cmd(self):
        assert self.storage.ex_telnet_cmd('pytest', 'lun show', self.oprt_id)

    def test_lun_create(self):
        assert self.storage.lun_create() == None
        self.storage.lun_destroy('pytest_99')

    def test_lun_map(self):
        self.storage.lun_create()
        assert self.storage.lun_map() == None
        self.storage.lun_unmap('pytest_99')
        self.storage.lun_destroy('pytest_99')

    def test_lun_unmap(self):
        self.storage.lun_create()
        self.storage.lun_map()
        assert self.storage.lun_unmap('pytest_99') == True
        self.storage.lun_destroy('pytest_99')

    def test_lun_destroy(self):
        self.storage.lun_create()
        assert self.storage.lun_destroy('pytest_99') == True

    def test_get_all_cfgd_lun(self):
        assert self.storage.get_all_cfgd_lun()

    def test_del_all(self):
        self.storage.lun_create()
        self.storage.lun_map()
        assert self.storage.del_all(['pytest_99']) == None
