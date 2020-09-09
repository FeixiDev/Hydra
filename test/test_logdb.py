import logdb
import sundry
import consts
import log

LOG_PATH = "./Hydra_log.log"
LOG_FILE_NAME = 'Hydra_log.log'


def test_prepare_db():
    assert logdb.prepare_db() == None


def test_isFileExists():
    assert logdb.isFileExists(LOG_PATH) == True


def test_fill_db_with_log():
    assert logdb._fill_db_with_log() == None


def test_read_log_files():
    assert logdb._read_log_files() != None


def test_get_log_files():
    assert logdb._get_log_files(LOG_FILE_NAME) == ['Hydra_log.log']


class TestLogDB:

    def setup_class(self):
        self.tid = consts.glo_tsc_id()
        self.logger = log.Log(self.tid)
        consts.set_glo_log(self.logger)
        self.logger.write_to_log('T', 'DATA', 'cmd', 'exception',
                            '100', {'valid': '1', 'cmd': 'pytest'})
        self.db = logdb.LogDB()
        logdb.prepare_db()
        sql = "SELECT id FROM logtable order by id desc"
        self.log_id = self.db.sql_fetch_one(sql)

    def test_insert_data(self):
        assert self.db.insert_data((None, '2020/09/07 15:59:54', '1599465591',
                                    'F', 'DATA', 'STR', '2ltpi6N3', '', '5994164559')) == None

    def test_create_table(self):
        assert self.db._create_table() == None

    def test_sql_fetch_one(self):
        sql = f"SELECT data FROM logtable WHERE type1 = 'DATA'"
        assert self.db.sql_fetch_one(sql) != None

    def test_sql_fetch_all(self):
        sql = f'SELECT DISTINCT transaction_id FROM logtable'
        assert self.db.sql_fetch_all(sql) != None

    def test_get_cmd_result(self):
        assert self.db.get_cmd_result(100) != None

    def test_find_oprt_id_via_string(self):
        assert self.db.find_oprt_id_via_string(self.tid, 'pytest') != None

    def test_get_anwser(self):
        assert self.db.get_anwser(self.tid) != None

    def test_get_transaction_id_via_date(self):
        dates = '2020/08/21 13:00:00'
        datee = '2020/08/23 15:00:00'
        assert self.db.get_transaction_id_via_date(dates, datee) != None

    def test_get_all_transaction(self):
        assert self.db.get_all_transaction() != None

    def test_get_cmd_via_tid(self):
        assert self.db.get_cmd_via_tid(
            self.tid) == "{'valid': '1', 'cmd': 'pytest'}"

    def test_get_time_via_str(self):
        assert self.db.get_time_via_str(self.tid, 'test') != None

    def test_get_exception_info(self):
        assert self.db.get_exception_info(self.tid) != None

    def test_get_oprt_id_via_db_id(self):
        assert self.db.get_oprt_id_via_db_id(self.tid, self.log_id) != None

    def test_drop_table(self):
        assert self.db._drop_table() == None
