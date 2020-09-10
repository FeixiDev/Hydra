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

    def test_create_map(self):
        assert self.storage.create_map() == None
        self.storage._unmap_lun('pytest_99')
        self.storage._destroy_lun('pytest_99')

    def test_create_lun(self):
        assert self.storage._create_lun('pytest_99') == None
        self.storage._destroy_lun('pytest_99')

    def test_map_lun(self):
        self.storage._create_lun('pytest_99')
        assert self.storage._map_lun('pytest_99') == None
        self.storage._unmap_lun('pytest_99')
        self.storage._destroy_lun('pytest_99')

    def test_unmap_lun(self):
        self.storage._create_lun('pytest_99')
        self.storage._map_lun('pytest_99')
        assert self.storage._unmap_lun('pytest_99') == True
        self.storage._destroy_lun('pytest_99')

    def test_destroy_lun(self):
        self.storage._create_lun('pytest_99')
        assert self.storage._destroy_lun('pytest_99') == True

    def test_get_all_cfgd_lun(self):
        assert self.storage.get_all_cfgd_lun()

    def test_del_luns(self):
        self.storage._create_lun('pytest_99')
        self.storage._map_lun('pytest_99')
        assert self.storage.del_luns(['pytest_99']) == None
