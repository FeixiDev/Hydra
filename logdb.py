import re
import os
import sqlite3
import consts

LOG_PATH = "./Hydra_log.log"
LOG_FILE_NAME = 'Hydra_log.log'

def prepare_db():
    db = LogDB()
    consts.set_glo_db(db)
    _fill_db_with_log()


def isFileExists(strfile):
    # 检查文件是否存在
    return os.path.isfile(strfile)

def _fill_db_with_log():
    id = (None,)
    re_ = re.compile(r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?\]?)\]\|',
                     re.DOTALL)

    db = consts.glo_db()
    all_log_data = _read_log_files()
    all_data = re_.findall(all_log_data)

    for data in all_data:
        data = id + data
        print(data)
        db.insert_data(data)

    db.con.commit()



def _read_log_files():
    all_data = ''
    if not isFileExists(LOG_PATH):
        print('no log file')
        return
    for file in _get_log_files(LOG_FILE_NAME):
        f = open('./' + file)
        data = f.read()
        all_data+=data
        f.close()
    return all_data


def _get_log_files(base_log_file):
    list_file = []
    all_file = (os.listdir('.'))
    for file in all_file:
        if base_log_file in file:
            list_file.append(file)
    list_file.sort(reverse=True)
    return list_file


class LogDB():
    create_table_sql = '''
    create table if not exists logtable(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time DATE(30),
        transaction_id varchar(20),
        display varchar(5),
        type1 TEXT,
        type2 TEXT,
        describe1 TEXT,
        describe2 TEXT,
        data TEXT
        );'''

    insert_sql = '''
    replace into logtable
    (
        id,
        time,
        transaction_id,
        display,
        type1,
        type2,
        describe1,
        describe2,
        data
        )
    values(?,?,?,?,?,?,?,?,?)
    '''

    drop_table_sql = "DROP TABLE if exists logtable "

    def __init__(self):
        self.con = sqlite3.connect("logDB.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self._drop_table()
        self._create_table()

    def insert_data(self, data):
        self.cur.execute(self.insert_sql, data)

    def _create_table(self):
        self.cur.execute(self.create_table_sql)
        self.con.commit()

    def _drop_table(self):
        self.cur.execute(self.drop_table_sql)
        self.con.commit()


    # 获取表单行数据的通用方法
    def sql_fetch_one(self, sql):
        self.cur.execute(sql)
        data_set = self.cur.fetchone()
        if data_set:
            if len(data_set) == 1:
                return data_set[0]
            else:
                return data_set
        else:
            return data_set

    # 获取表全部数据的通用方法
    def sql_fetch_all(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchall()
        return list(date_set)

    def get_cmd_result(self, oprt_id):
        sql = f"SELECT data FROM logtable WHERE type1 = 'DATA' and type2 = 'cmd' and describe2 = '{oprt_id}'"
        return self.sql_fetch_one(sql)


    def find_oprt_id_via_string(self, transaction_id, string):
        id_now = consts.glo_log_id()
        sql = f"SELECT id,data FROM logtable WHERE describe1 = '{string}' and id > {id_now} and transaction_id = '{transaction_id}'"
        id_and_oprt_id = self.sql_fetch_one(sql)
        if id_and_oprt_id:
            return id_and_oprt_id
        else:
            return ('','')

    def get_anwser(self, transaction_id):
        sql = f"SELECT time,data FROM logtable WHERE transaction_id = '{transaction_id}' and describe2 = 'confirm deletion'"
        result = self.sql_fetch_one(sql)
        if result:
            return result
        else:
            return ('', '')

    def get_transaction_id_via_date(self, date_start, date_end):
        # 获取一个时间段内的全部事务id
        sql = f"SELECT DISTINCT transaction_id FROM logtable WHERE time >= '{date_start}' and time <= '{date_end}'"
        result = self.sql_fetch_all(sql)
        list_result = []
        if result:
            for i in result:
                list_result.append(i[0])
            return list_result
        return []

    def get_all_transaction(self):
        sql = f'SELECT DISTINCT transaction_id FROM logtable'
        result = self.sql_fetch_all(sql)
        list_result = []
        if result:
            for i in result:
                list_result.append(i[0])
            return list_result
        return []

    def get_cmd_via_tid(self, transaction_id):
        sql = f"SELECT data FROM logtable WHERE transaction_id = '{transaction_id}'"
        return self.sql_fetch_one(sql)

    def get_time_via_str(self, transaction_id , str):
        id_now = consts.glo_log_id()
        sql = f"SELECT time FROM logtable WHERE transaction_id = '{transaction_id}' and id >= {id_now} and data LIKE '%{str}%'"
        return self.sql_fetch_one(sql)

    def get_exception_info(self,transaction_id):
        id_now = consts.glo_log_id()
        sql = f"SELECT data FROM logtable WHERE transaction_id = '{transaction_id}' and describe1 = 'exception' and id >= {id_now}"
        return self.sql_fetch_one(sql)

    def get_oprt_id_via_db_id(self,transaction_id,db_id):
        sql = f"SELECT data FROM logtable WHERE transaction_id = '{transaction_id}' and id = {db_id}"
        return self.sql_fetch_one(sql)


if __name__ == '__main__':
    pass


