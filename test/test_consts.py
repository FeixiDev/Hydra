import consts


def test_init():
    assert consts._init() == None


def test_set_value():
    assert consts.set_value('testkey', 'testvalue') == None


def test_get_value():
    assert consts.get_value('testkey') == 'testvalue'
    assert consts.get_value('key') == None


def test_set_glo_log():
    consts.set_glo_log('testLOG')
    assert consts._global_dict['LOG'] == 'testLOG'


def test_set_glo_db():
    consts.set_glo_db('testDB')
    assert consts._global_dict['DB'] == 'testDB'


def test_set_glo_str():
    consts.set_glo_str('testSTR')
    assert consts._global_dict['STR'] == 'testSTR'


def test_set_glo_id():
    consts.set_glo_id('testID')
    assert consts._global_dict['ID'] == 'testID'


def test_set_glo_rpl():
    consts.set_glo_rpl('testRPL')
    assert consts._global_dict['RPL'] == 'testRPL'


def test_set_glo_tsc_id():
    consts.set_glo_tsc_id('testTSC_ID')
    assert consts._global_dict['TSC_ID'] == 'testTSC_ID'


def test_set_glo_log_id():
    consts.set_glo_log_id('testLOG_ID')
    assert consts._global_dict['LOG_ID'] == 'testLOG_ID'


def test_set_glo_log_switch():
    consts.set_glo_log_switch('testLOG_SWITCH')
    assert consts._global_dict['LOG_SWITCH'] == 'testLOG_SWITCH'


def test_set_glo_id_list():
    consts.set_glo_id_list('testID_LIST')
    assert consts._global_dict['ID_LIST'] == 'testID_LIST'


def test_glo_log():
    assert consts.glo_log() == 'testLOG'


def test_glo_db():
    assert consts.glo_db() == 'testDB'


def test_glo_str():
    assert consts.glo_str() == 'testSTR'


def test_glo_id():
    assert consts.glo_id() == 'testID'


def test_glo_rpl():
    assert consts.glo_rpl() == 'testRPL'


def test_glo_tsc_id():
    assert consts.glo_tsc_id() == 'testTSC_ID'


def test_glo_log_id():
    assert consts.glo_log_id() == 'testLOG_ID'


def test_glo_log_switch():
    assert consts.glo_log_switch() == 'testLOG_SWITCH'


def test_glo_id_list():
    assert consts.glo_id_list() == 'testID_LIST'


def test_get_cmd_debug_sys():
    assert 'echo -- date&time: >> testfolder/sys_info.log' in consts.get_cmd_debug_sys(
        'testfolder', 'testhost')


def test_get_cmd_debug_drbd():
    assert 'drbdadm status >> testfolder/drbd.log' in consts.get_cmd_debug_drbd(
        'testfolder', 'testhost')


def test_get_cmd_debug_crm():
    assert 'crm res show >> testfolder/crm.log' in consts.get_cmd_debug_crm(
        'testfolder', 'testhost')


def test_get_cmd_debug_stor():
    assert 'iscsi initiator show' in consts.get_cmd_debug_stor()
