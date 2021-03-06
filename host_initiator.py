# coding:utf-8
import connect
import time
import sundry as s
import consts

SSH = None

VPLX_IP = '10.203.1.199'
HOST = '10.203.1.200'
PORT = 22
USER = 'root'
PASSWORD = 'password'
TIMEOUT = 3
MOUNT_POINT = '/mnt'
TARGET_IQN='iqn.2020-06.com.example:test-max-lun'

def init_ssh():
    global SSH
    if not SSH:
        SSH = connect.ConnSSH(HOST, PORT, USER, PASSWORD, TIMEOUT)
    else:
        pass

def umount_mnt():
    SSH.execute_command(f'umount {MOUNT_POINT}')

def change_iqn(iqn):
    iscsi=s.Iscsi(SSH, VPLX_IP)
    s.pwl('Start to modify IQN on Host', 1, '', 'start')
    iscsi.modify_iqn(iqn)

def rescan_after_remove():
    '''
    vplx rescan after delete
    '''
    s.scsi_rescan(SSH, 'r')

class DebugLog(object):
    def __init__(self):
        init_ssh()
        self.tid = consts.glo_tsc_id()
        self.debug_folder = f'/var/log/{self.tid}'
        self.dbg = s.DebugLog(SSH, self.debug_folder, HOST)

    def collect_debug_sys(self):
        cmd_debug_sys = consts.get_cmd_debug_sys(self.debug_folder)
        self.dbg.prepare_debug_log(cmd_debug_sys)

    def get_all_log(self, folder):
        local_file = f'{folder}/{HOST}.tar'
        self.dbg.get_debug_log(local_file)


class HostTest(object):
    '''
    Format, write, and read iSCSI LUN
    '''
    def __init__(self):
        self.logger = consts.glo_log()
        self.rpl = consts.glo_rpl()
        self._prepare()
        self.iscsi=s.Iscsi(SSH,VPLX_IP)

    def _prepare(self):
        if self.rpl == 'no':
            init_ssh()
            umount_mnt()

    def _mount(self, dev_name):
        '''
        Mount disk
        '''
        oprt_id = s.get_oprt_id()
        unique_str = '6CJ5opVX'
        cmd = f'mount {dev_name} {MOUNT_POINT}'
        s.pwl(f'Start to mount "{dev_name}" to "{MOUNT_POINT}"', 2, oprt_id, 'start')
        result_mount = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result_mount:
            if result_mount['sts']:
                s.pwl(f'Disk "{dev_name}" mounted to "{MOUNT_POINT}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to mount "{dev_name}" to "{MOUNT_POINT}"', 3, 2)
        else:
            s.handle_exception()

    def _judge_format(self, string):
        '''
        Determine the format status
        '''
        re_string = r'done'
        re_resulgt = s.re_findall(re_string, string)
        if len(re_resulgt) == 4:
            return True

    def _format(self, dev_name):
        '''
        Format disk and mount disk
        '''
        cmd = f'mkfs.ext4 {dev_name} -F'
        oprt_id = s.get_oprt_id()
        s.pwl(f'Start to format "{dev_name}"', 2, oprt_id, 'start')
        result_format = s.get_ssh_cmd(SSH, '7afztNL6', cmd, oprt_id)
        if result_format:
            if result_format['sts']:
                result_format = result_format['rst'].decode('utf-8')
                if self._judge_format(result_format):
                    s.pwl(f'Succeed in formatting "{dev_name}"', 3, oprt_id, 'finish')
                    return True
                else:
                    s.pwce(f'Failed to format "{dev_name}"', 3, 2)
            else:
                s.pwce(f'Failed to execute command:"{cmd}"', 3, 2)
        else:
            s.handle_exception()

    def _get_test_perf(self, cmd_dd, unique_str):
        '''
        Use regular to get the speed of test
        '''
        result_dd = s.get_ssh_cmd(SSH, unique_str, cmd_dd, s.get_oprt_id())
        result_dd = result_dd['rst'].decode('utf-8')
        re_performance = r'.*s, ([0-9.]* [A-Z]B/s)'
        re_result = s.re_findall(re_performance, result_dd)
        # 正则相关的暂时不做记录
        # self.logger.write_to_log('T', 'OPRT', 'regular', 'findall', oprt_id, {
        #                          re_performance: result_dd})
        if re_result:
            dd_perf = re_result[0]
            # self.logger.write_to_log(
            #     'F', 'DATA', 'regular', 'findall', oprt_id, dd_perf)
            return dd_perf
        else:
            s.pwce('Can not get test result', 3, 2)

    def _write_test(self):
        cmd_dd_write = f'dd if=/dev/zero of={MOUNT_POINT}/t.dat bs=512k count=16'
        write_perf = self._get_test_perf(cmd_dd_write, unique_str='CwS9LYk0')
        s.pwl(f'Write Speed: {write_perf}', 3, '', 'finish')

    def _read_test(self):
        cmd_dd_read = f'dd if={MOUNT_POINT}/t.dat of=/dev/zero bs=512k count=16'
        read_perf = self._get_test_perf(cmd_dd_read, unique_str='hsjG0miU')
        s.pwl(f'Read  Speed: {read_perf}', 3, '', 'finish')

    def _mount_disk(self):
        gnd = s.GetNewDisk(SSH, VPLX_IP)
        dev_name = gnd.get_disk_from_vplx()
        if self._format(dev_name):
            if self._mount(dev_name):
                return True
            # else:
            #     s.pwce(f'Failed to mount device "{dev_name}"', 3, 2)
        # else:
        #     s.pwce(f'Failed to format device "{dev_name}"', 3, 2)

    def io_test(self):
        time.sleep(0.5)
        s.pwl('Start to format，write and read the LUN on Host', 0, s.get_oprt_id(), 'start')
        self._mount_disk()
        s.pwl(f'Start speed test', 2, '', 'start')
        self._write_test()
        self._read_test()



if __name__ == "__main__":
    pass
  