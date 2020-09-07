#  coding: utf-8
import random
import consts
import sys
import re
import time
import traceback
from random import shuffle
import debug_log
import sundry as s

TARGET_IQN='iqn.2020-06.com.example:test-max-lun'

def record_exception(func):
    """
    Decorator
    Get exception, throw the exception after recording
    :param func:Command binding function
    """
    def wrapper(self, *args):
        try:
            return func(self, *args)
        except Exception as e:
            self.logger.write_to_log(
                'F', 'DATA', 'debug', 'exception', '', str(traceback.format_exc()))
            raise e
    return wrapper

def pick_iqns_random(random_num):
    iqn_list = consts.glo_iqn_list()
    iqn_random_list = sorted(random.sample(iqn_list, random_num))
    return iqn_random_list

def generate_iqn(num):
    lun_id=consts.glo_id()
    iqn=f"iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:{lun_id}-{num}"
    return iqn

def generate_iqn_list(capacity):
    consts.set_glo_iqn_list([])
    for iqn_id in range(capacity):
        iqn = generate_iqn(iqn_id)
        consts.append_glo_iqn_list(iqn)

def id_str_to_list(id_range):
    id_list = []
    id_range_list=[int(i) for i in id_range]
    if len(id_range_list) not in [1, 2]:
        pwce('Please verify id format', 2, 2)
    elif len(id_range_list) == 1:
        id_list = id_range_list
    elif len(id_range_list) == 2:
        for id in range(id_range_list[0], id_range_list[1] + 1):
            id_list.append(id)
    return id_list

def scsi_rescan(ssh, mode):
    cmd=''
    if mode == 'n':
        cmd = '/usr/bin/rescan-scsi-bus.sh'
        pwl('Start to scan SCSI device with normal way', 3, '', 'start')
    elif mode == 'r':
        cmd = '/usr/bin/rescan-scsi-bus.sh -r'
        pwl('Start to scan SCSI device after removing disk', 2, '', 'start')
    elif mode == 'a':
        cmd = '/usr/bin/rescan-scsi-bus.sh -a'
        pwl('Start to scan SCSI device in depth', 3, '', 'start')
    if consts.glo_rpl() == 'no':
        result = ssh.execute_command(cmd)
        if result:
            if result['sts']:
                return True
            else:
                pwe('Failed to scan SCSI device', 4, 2)
        else:
            handle_exception()
    else:
        return True

def re_search(re_string, tgt_string):
    logger = consts.glo_log()
    oprt_id = get_oprt_id()
    logger.write_to_log('T', 'OPRT', 'regular', 'search',
                        oprt_id, {re_string: tgt_string})
    re_object = re.compile(re_string)
    re_result = re_object.search(tgt_string)
    logger.write_to_log('F', 'DATA', 'regular', 'search', oprt_id, re_result)
    return re_result

def get_ssh_cmd(ssh_obj, unique_str, cmd, oprt_id):
    """
    Execute command on ssh connected host.If it is replay mode, get relevant data from the log.
    :param ssh_obj:SSH connection object
    :param unique_str:The specific character described in the method calling this function
    :param cmd:Command to be executed
    :param oprt_id:The unique id for the operation here
    :return:Command execution result
    """
    logger = consts.glo_log()
    global RPL
    RPL = consts.glo_rpl()
    if RPL == 'no':
        logger.write_to_log('F', 'DATA', 'STR', unique_str, '', oprt_id)
        logger.write_to_log('T', 'OPRT', 'cmd', 'ssh', oprt_id, cmd)
        result_cmd = ssh_obj.execute_command(cmd)
        logger.write_to_log('F', 'DATA', 'cmd', 'ssh', oprt_id, result_cmd)
        return result_cmd
    elif RPL == 'yes':
        db = consts.glo_db()
        db_id, oprt_id = db.find_oprt_id_via_string(
            consts.glo_tsc_id(), unique_str)
        result_cmd = db.get_cmd_result(oprt_id)
        if result_cmd:
            result = eval(result_cmd)
        else:
            result = None
        if db_id:
            change_pointer(db_id)
        return result

def get_telnet_cmd(telnet_obj, unique_str, cmd, oprt_id):
    logger = consts.glo_log()
    global RPL
    RPL = consts.glo_rpl()
    if RPL == 'no':
        logger.write_to_log(
            'F', 'DATA', 'STR', unique_str, '', oprt_id)
        logger.write_to_log(
            'T', 'OPRT', 'cmd', 'telnet', oprt_id, cmd)
        result = telnet_obj.execute_command(cmd)
        logger.write_to_log(
            'F', 'DATA', 'cmd', 'telnet', oprt_id, result)
        return result

    elif RPL == 'yes':
        db = consts.glo_db()
        db_id, oprt_id = db.find_oprt_id_via_string(consts.glo_tsc_id(), unique_str)
        if db_id:
            change_pointer(db_id)
        result_cmd = db.get_cmd_result(oprt_id)
        if result_cmd:
            return result_cmd

def _compare(name, name_list):
    if name in name_list:
        return name
    elif 'res_' + name in name_list:
        return 'res_' + name

def get_to_del_list(name_list):
    '''
    Get the list of the resource which will be deleted.
    : Get the resource according to the unique_string and unique_id，and check whether it is exist.
    '''
    uni_str = consts.glo_str()
    id_list = consts.glo_id_list()
    to_del_list = []

    if uni_str and id_list:
        for id_ in id_list:
            str_ = f'{uni_str}_{id_}'
            name = _compare(str_, name_list)
            if name:
                to_del_list.append(name)
    elif uni_str:
        for name in name_list:
            if uni_str in name:
                to_del_list.append(name)
    elif id_list:
        for id_ in id_list:
            str_ = f'_{id_}'
            for name in name_list:
                if name.endswith(str_):
                    to_del_list.append(name)
    else:
        to_del_list = name_list
    return to_del_list

def prt_res_to_del(str_, res_list):
    print(f'{str_:<15} to be delete:')
    print('-------------------------------------------------------------')
    for i in range(len(res_list)):
        res_name = res_list[i]
        print(f'{res_name:<18}', end='')
        if (i + 1) % 5 == 0:
            print()
    print()

def get_transaction_id():
    return str(int(time.time()))

def get_oprt_id():
    time_stamp = str(get_transaction_id())
    str_list = list(time_stamp)
    shuffle(str_list)
    return ''.join(str_list)

# def get_username():
#     return getpass.getuser()
#
#
# def get_hostname():
#     return socket.gethostname()
#
#
# # Get the path of the program
#
#
# def get_path():
#     return os.getcwd()

def change_pointer(new_id):
    consts.set_glo_log_id(new_id)

def re_findall(re_string, tgt_string):
    logger = consts.glo_log()
    oprt_id = get_oprt_id()
    logger.write_to_log('T', 'OPRT', 'regular', 'findall',
                        oprt_id, {re_string: tgt_string})
    re_object = re.compile(re_string)
    re_result = re_object.findall(tgt_string)
    logger.write_to_log('F', 'DATA', 'regular', 'findall', oprt_id, re_result)
    return re_result

def ran_str(num):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    str_ = ''
    for i in range(num):
        str_ += random.choice(chars)
    return str_

def prt(str, level=0, warning_level=0):
    if isinstance(warning_level, int):
        warning_str = '*' * warning_level
    else:
        warning_str = ''
    indent_str = '  ' * level + str
    title_str = '---- ' + str + ' '
    rpl = consts.glo_rpl()
    if rpl == 'no':
        if level == 0:
            print()
            print(f'{title_str:-<80}')
        else:
            print(f'|{warning_str:<4}{indent_str:<70}{warning_str:>4}|')
    else:
        if warning_level == 'exception':
            print(' exception infomation '.center(105, '*'))
            print(str)
            print(f'{" exception infomation ":*^105}', '\n')
            return

        db = consts.glo_db()
        time = db.get_time_via_str(consts.glo_tsc_id(), str)
        if not time:
            time = ''

        if level == 0:
            print(f'{title_str:-<105}')
        else:
            print(f'|{warning_str:<4} Re:{time:<20} {indent_str:<70}{warning_str:>4}|')

def pwl(str, level, oprt_id=None, type=None):
    # rpl = 'no'
    rpl = consts.glo_rpl()
    if rpl == 'no':
        logger = consts.glo_log()
        prt(str, level)
        logger.write_to_log('T', 'INFO', 'info', type, oprt_id, str)

    elif rpl == 'yes':
        prt(str, level)

def prt_log(str, level, warning_level):
    """
    print, write to log and exit.
    :param logger: Logger object for logging
    :param print_str: Strings to be printed and recorded
    """
    logger = consts.glo_log()

    #-m:这里也是要调用s.prt还是啥,指定级别,不同地方调用要用不同的级别.
    rpl = consts.glo_rpl()
    format_width = 80
    if rpl == 'yes':
        format_width = 105
        db = consts.glo_db()
        oprt_id = db.get_oprt_id_via_db_id(consts.glo_tsc_id(), consts.glo_log_id())
        prt(str + f'.oprt_id:{oprt_id}', level, warning_level)
    elif rpl == 'no':
        prt(str, level, warning_level)

    if warning_level == 1:
        logger.write_to_log('T', 'INFO', 'warning', 'fail', '', str)
    elif warning_level == 2:
        logger.write_to_log('T', 'INFO', 'error', 'exit', '', str)
        # print(f'{"":-^{format_width}}','\n')
        # sys.exit()

def pwe(str, level, warning_level):
    rpl = consts.glo_rpl()
    prt_log(str, level, warning_level)

    if warning_level == 2:
        if rpl == 'no':
            sys.exit()
        else:
            raise consts.ReplayExit

def pwce(str, level, warning_level):
    """
    print, write to log and exit.
    :param logger: Logger object for logging
    :param print_str: Strings to be printed and recorded
    """
    rpl = consts.glo_rpl()
    prt_log(str,level,warning_level)
    if rpl == 'no':
        debug_log.collect_debug_log()
        print('debug')
        sys.exit()
    else:
        raise consts.ReplayExit

def handle_exception(str='',level=0,warning_level=0):
    rpl = consts.glo_rpl()
    if rpl == 'yes':
        db = consts.glo_db()
        exception_info = db.get_exception_info(consts.glo_tsc_id())
        if exception_info:
            prt('The transaction was interrupted because of an exception',1,warning_level=2)
            prt(exception_info, warning_level='exception')
            raise consts.ReplayExit
        else:
            oprt_id = db.get_oprt_id_via_db_id(consts.glo_tsc_id(),consts.glo_log_id())
            prt(f'Unable to get data from the logfile.oprt_id:{oprt_id}',3,2)
            raise consts.ReplayExit

    else:
        pwce(str,level,warning_level)

def get_answer(str_input):
    logger = consts.glo_log()
    rpl = consts.glo_rpl()
    logdb = consts.glo_db()
    transaction_id = consts.glo_tsc_id()
    if rpl == 'no':
        answer = input(str_input)
        logger.write_to_log('F' ,'DATA', 'INPUT', 'confirm_input', 'confirm deletion', answer)
    else:
        print(str_input)
        time, answer = logdb.get_anwser(transaction_id)
        if not time:
            time = ''
        print(f'RE:{time:<20} 用户输入: {answer}')
    return answer

def get_tid_list(args, db_obj):
    tid_list=[]
    if args.tid:
        tid_list.append(args.tid)
    elif args.date:
        tid_list = db_obj.get_transaction_id_via_date(
            args.date[0], args.date[1])
    elif args.all:
        tid_list = db_obj.get_all_transaction()
    return tid_list


class GetNewDisk():
    def __init__(self, ssh_obj, target_ip):
        self.ssh_obj = ssh_obj
        self.iscsi = Iscsi(ssh_obj, target_ip)

    def get_disk_from_netapp(self):
        self.iscsi.create_session()
        s.pwl(f'Start to get the disk device with id {consts.glo_id()} on VersaPLX', 2, '', 'start')
        blk_dev_name = self._get_disk_dev('NETAPP')
        return blk_dev_name

    def get_disk_from_vplx(self):
        self.iscsi.create_session()
        s.pwl(f'Start to get the disk device with id {consts.glo_id()} on Host', 2, '', 'start')
        dev_name = self._get_disk_dev('LIO-ORG')
        return dev_name

    def _find_new_disk(self, string):
        id = consts.glo_id()
        result_lsscsi = self._get_lsscsi(self.ssh_obj, 'D37nG6Yi', get_oprt_id())
        re_string = f'\:{id}\].*{string}[ 0-9a-zA-Z._]*(/dev/sd[a-z]{{1,3}})'
        disk_dev = re_search(re_string, result_lsscsi)
        if disk_dev:
            return disk_dev.group(1)

    def _get_disk_dev(self, dev_vendor):
        scsi_rescan(self.ssh_obj, 'n')
        disk_dev = self._find_new_disk(dev_vendor)
        if disk_dev:
            pwl(f'Succeed in getting disk device "{disk_dev}" with id "{consts.glo_id()}"', 4, '', 'finish')
            return disk_dev
        else:
            pwl(f'No disk with SCSI ID "{consts.glo_id()}" found, scan again...', 4, '', 'start')
            scsi_rescan(self.ssh_obj, 'a')
            disk_dev = self._find_new_disk(dev_vendor)
            if disk_dev:
                pwl(f'Succeed in getting the disk device "{disk_dev}" with id "{consts.glo_id()}"', 4, '', 'finish')
                return disk_dev
            else:
                pwce('No disk found, exit the program', 4, 2)

    def _get_lsscsi(self, ssh, func_str, oprt_id):
        pwl('Start to get the list of all SCSI device', 3, oprt_id, 'start')
        cmd_lsscsi = 'lsscsi'
        result_lsscsi = get_ssh_cmd(ssh, func_str, cmd_lsscsi, oprt_id)
        if result_lsscsi:
            if result_lsscsi['sts']:
                return result_lsscsi['rst'].decode('utf-8')
            else:
                pwe(f'Failed to excute Command "{cmd_lsscsi}"', 4, 1)
        else:
            handle_exception()



class DebugLog(object):
    def __init__(self, ssh_obj, debug_folder, host):
        # print(debug_folder)
        self.dbg_folder = debug_folder
        self.SSH = ssh_obj
        self.host = host
        self._mk_debug_folder()

    def _mk_debug_folder(self):
        # -m:增加判断, 用file命令结果判断, 如果已存在,则不创建
        print('self.dbg_folder',self.dbg_folder)
        output = self.SSH.execute_command(f'mkdir {self.dbg_folder}')
        self.SSH.execute_command(f'mkdir {self.dbg_folder}/{self.host}')
        if output['sts']:
            pass
        else:
            prt(f'Can not create folder {self.dbg_folder} to stor debug log', 3, 2)
            sys.exit()

    def prepare_debug_log(self, cmd_list):
        for cmd in cmd_list:
            output = self.SSH.execute_command(cmd)
            if output['sts']:
                time.sleep(0.1)
            else:
                prt(f'Collect log command "{cmd}" execute failed.', 3, 2)

    #未改，需要了解返回值
    def get_debug_log(self, local_folder):
        dbg_file = f'{self.dbg_folder}.tar'
        self.SSH.execute_command(f'mv {self.dbg_folder}/*.log {self.dbg_folder}/{self.host}')
        self.SSH.execute_command(f'mv {self.dbg_folder}/*.tar {self.dbg_folder}/{self.host}')
        self.SSH.execute_command(f'tar cvf {dbg_file} -C {self.dbg_folder} {self.host}')
        self.SSH.download(dbg_file, local_folder)

class Iscsi(object):
    def __init__(self,ssh_obj,tgt_ip):
        self.SSH = ssh_obj
        self.tgt_ip=tgt_ip

    def create_session(self):
        if not self._find_session():
            if self.login():
                return True
        else:
            pwl(f'The iSCSI session already logged in to {self.tgt_ip}', 3)
            return True

    def _end_session(self,tgt_iqn):
        if self._find_session():
            if self._logout(tgt_iqn):
                return True
        else:
            pwl(f'The iSCSI session already logged out to {self.tgt_ip}', 3)
            return True
    
    def _logout(self,tgt_iqn):
        cmd=f'iscsiadm -m node -T {tgt_iqn} --logout'
        oprt_ip=get_oprt_id()
        pwl(f'Start to logout "{self.tgt_ip}"', 2, '', 'start')
        results=get_ssh_cmd(self.SSH,'HuTg1LaQ', cmd, oprt_ip)
        if results:
            if results['sts']:
                re_string=f'Logout of.*portal: ({self.tgt_ip}).*successful'
                re_result=re_search(re_string,results['rst'].decode('utf-8'))
                if re_result:
                    pwl(f'Success in logout {self.tgt_ip}', 3, '', 'finish')
                    return True
                else:
                    pwce(f'Failed to logout {self.tgt_ip}', 3, 2)
        else:
            handle_exception()

    def login(self):
        '''
        Discover iSCSI login session, if no, login to vplx
        '''
        oprt_id = get_oprt_id()
        cmd = f'iscsiadm -m discovery -t st -p {self.tgt_ip} -l'
        pwl(f'Start to login "{self.tgt_ip}"', 2, '', 'start')
        result_iscsi_login = get_ssh_cmd(self.SSH, 'rgjfYl3K', cmd, oprt_id)
        if result_iscsi_login:
            if result_iscsi_login['sts']:
                result_iscsi_login = result_iscsi_login['rst'].decode('utf-8')
                re_string = f'Login to.*portal: ({self.tgt_ip}).*successful'
                if re_search(re_string, result_iscsi_login):
                    pwl(f'Success in logging to {self.tgt_ip}',3,'','finish')
                    return True
                else:
                    pwce(f'Failed to login {self.tgt_ip}',3,warning_level=2)

        else:
            handle_exception()

    # -m:string 和 oprt id 不用传递过来,在内部定义即可
    def _find_session(self):
        '''
        Execute the command and check up the status of session
        '''
        oprt_id = get_oprt_id()
        cmd = 'iscsiadm -m session'
        pwl(f'Check up the status of session', 2, '', 'start')
        result_session = get_ssh_cmd(self.SSH, 'V9jGOP1i', cmd, oprt_id)
        if result_session:
            if result_session['sts']:
                result_session = result_session['rst'].decode('utf-8')
                re_session = f'tcp:.*({self.tgt_ip}):.*'
                if re_search(re_session, result_session):
                    pwl(f'Found session connected to "{self.tgt_ip}"', 3, '', 'start')
                    return True
                else:
                    pwl(f'Not found session connected to "{self.tgt_ip}"', 3, '', 'start')
            else:
                pwl(f'Not found session connected to "{self.tgt_ip}"', 3, '', 'start')
        else:
            handle_exception()

    def modify_iqn(self, iqn):
        self._end_session(TARGET_IQN)
        self._modify_iqn_cfg_file(iqn)
        self._restart_service()

    def _restart_service(self):
        cmd=f'systemctl restart iscsid open-iscsi'
        oprt_id=get_oprt_id()
        pwl('Start to restart iscsi service', 2, '', 'start')
        results=get_ssh_cmd(self.SSH,'Uksjdkqi',cmd,oprt_id)
        if results:
            if results['sts']:
                pwl('Success in restarting iscsi service',3,'','finish')
                return True
            else:
                pwe('Failed to restart iscsi service',3,2)
        else:
            handle_exception()

    def _modify_iqn_cfg_file(self, iqn):
        cmd=f'echo "InitiatorName={iqn}" > /etc/iscsi/initiatorname.iscsi'
        oprt_id=get_oprt_id()
        pwl(f'Start to modify initiator IQN "{iqn}"', 2, '', 'start')
        results=get_ssh_cmd(self.SSH,'RTDAJDas',cmd,oprt_id)
        if results:
            if results['sts']:
                pwl(f'Success in modifying initiator IQN "{iqn}"',3,'','finish')
                return True
            else:
                pwe(f'Failed to modify initiator IQN "{iqn}"',3,2)
        else:
            handle_exception()




if __name__ == '__main__':
    pass
