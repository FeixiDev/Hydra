#  coding: utf-8
import connect
import sundry as s
import time
import consts
import log
import re

SSH = None

HOST = '10.203.1.199'
PORT = 22
USER = 'root'
PASSWORD = 'password'
TIMEOUT = 3

NETAPP_IP = '10.203.1.231'
TARGET_IQN = "iqn.2020-06.com.example:test-max-lun"
TARGET_NAME = 't_test'
PORTBLOCK_UNBLOCK_NAME="p_iscsi_portblock_off"


def init_ssh():
    global SSH
    if not SSH:
        SSH = connect.ConnSSH(HOST, PORT, USER, PASSWORD, TIMEOUT)

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

    def collect_debug_drbd(self):
        cmd_debug_drbd = consts.get_cmd_debug_drbd(self.debug_folder)
        self.dbg.prepare_debug_log(cmd_debug_drbd)

    def collect_debug_crm(self):
        cmd_debug_crm = consts.get_cmd_debug_crm(self.debug_folder)
        self.dbg.prepare_debug_log(cmd_debug_crm)

    def get_all_log(self, folder):
        local_file = f'{folder}/{HOST}.tar'
        self.dbg.get_debug_log(local_file)


class VplxDrbd(object):
    '''
    Integrate LUN in DRBD resources
    '''
    def __init__(self):
        self.logger = consts.glo_log()
        self.rpl = consts.glo_rpl()
        self.id = consts.glo_id()
        self.str = consts.glo_str()
        self._prepare()

    def _prepare(self):
        if self.rpl == 'no':
            init_ssh()

    def cfg(self):
        time.sleep(0.5)
        s.pwl('Start to configure DRDB resource and CRM resource on VersaPLX', 0, s.get_oprt_id(), 'start')
        s.pwl('Start to configure DRBD resource', 1, '', 'start')
        res_name = f'res_{self.str}_{self.id}'
        # global DRBD_DEV_NAME
        # DRBD_DEV_NAME = f'drbd{self.id}'
        self._add_config_file(res_name)  # 创建配置文件
        self._init(res_name)
        self._up(res_name)
        self._primary(res_name)
        self.status_verify(res_name)  # 验证有没有启动（UptoDate）

    def _add_config_file(self, res_name):
        '''
        Prepare DRDB resource config file
        '''
        blk_dev_name = s.GetNewDisk(SSH, NETAPP_IP).get_disk_from_netapp()
        self._create_config_file(blk_dev_name, res_name)

    def _create_config_file(self, blk_dev_name, res_name):
        s.pwl(f'Start to prepare DRBD config file "{res_name}.res"', 2, '', 'start')
        drbd_dev_name = f'drbd{self.id}'
        context = [rf'resource {res_name} {{',
                   rf'\ \ \ \ on maxluntarget {{',
                   rf'\ \ \ \ \ \ \ \ device /dev/{drbd_dev_name}\;',
                   rf'\ \ \ \ \ \ \ \ disk {blk_dev_name}\;',
                   rf'\ \ \ \ \ \ \ \ address 10.203.1.199:7789\;',
                   rf'\ \ \ \ \ \ \ \ node-id 0\;',
                   rf'\ \ \ \ \ \ \ \ meta-disk internal\;',
                   r'\ \ \ \}',
                   r'}']
        if self.rpl == 'yes':
            return
        self.logger.write_to_log(
            'F', 'DATA', 'value', 'list', 'content of drbd config file', context)
        unique_str = 'UsKyYtYm1'
        config_file_name = f'{res_name}.res'
        for i in range(len(context)):
            if i == 0:
                oprt_id = s.get_oprt_id()
                cmd = f'echo {context[i]} > /etc/drbd.d/{config_file_name}'
                echo_result = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
            else:
                oprt_id = s.get_oprt_id()
                cmd = f'echo {context[i]} >> /etc/drbd.d/{config_file_name}'
                echo_result = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
            if echo_result:
                if echo_result['sts']:
                    continue
                else:
                    s.pwce(f'Failed to prepare DRBD config file "{config_file_name}"', 3, 2)
            else:
                s.handle_exception()

        s.pwl(f'Succeed in creating DRBD config file "{config_file_name}"', 3, '', 'finish')

    def _init(self, res_name):
        '''
        Initialize DRBD resource
        '''
        oprt_id = s.get_oprt_id()
        unique_str = 'usnkegs'
        cmd = f'drbdadm create-md {res_name}'
        s.pwl(f'Start to initialize DRBD resource for "{res_name}"', 2, oprt_id, 'start')
        init_result = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        re_drbd = 'New drbd meta data block successfully created'
        if init_result:
            if init_result['sts']:
                re_result = s.re_search(re_drbd, init_result['rst'].decode())
                if re_result:
                    s.pwl(f'Succeed in initializing DRBD resource "{res_name}"', 3, oprt_id, 'finish')
                    return True
                else:
                    s.pwce(f'Failed to initialize DRBD resource {res_name}', 3, 2)
        else:
            s.handle_exception()

    def _up(self, res_name):
        '''
        Start DRBD resource
        '''
        oprt_id = s.get_oprt_id()
        unique_str = 'elsflsnek'
        cmd = f'drbdadm up {res_name}'
        s.pwl(f'Start to bring up DRBD resource "{res_name}"', 2, oprt_id, 'start')
        result = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result:
            if result['sts']:
                s.pwl(f'Succeed in bringing up DRBD resource "{res_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to bring up DRBD resource "{res_name}"', 3, 2)
        else:
            s.handle_exception()

    def _primary(self, res_name):
        '''
        Complete initial synchronization of resources
        '''
        oprt_id = s.get_oprt_id()
        unique_str = '7C4LU6Xr'
        cmd = f'drbdadm primary --force {res_name}'
        s.pwl(f'Start to initial synchronization for "{res_name}"', 2, oprt_id, 'start')
        result = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result:
            if result['sts']:
                s.pwl(f'Succeed in synchronizing DRBD resource "{res_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to synchronize DRBD resource "{res_name}"', 3, 2)
        else:
            s.handle_exception()

    def status_verify(self, res_name):
        '''
        Check DRBD resource status and confirm the status is UpToDate
        '''
        oprt_id = s.get_oprt_id()
        cmd = f'drbdadm status {res_name}'
        s.pwl(f'Start to check DRBD resource "{res_name}" status', 2, oprt_id, 'start')
        result = s.get_ssh_cmd(SSH, 'By91GFxC', cmd, oprt_id)
        if result:
            if result['sts']:
                result = result['rst'].decode()
                re_display = r'''disk:(\w*)'''
                re_result = s.re_search(re_display, result)
                if re_result:
                    status = re_result.group(1)
                    if status == 'UpToDate':
                        s.pwl(f'Succeed in checking DRBD resource "{res_name}" status', 3, oprt_id, 'finish')
                        return True
                    else:
                        s.pwce(f'Failed to check DRBD resource "{res_name}" status', 3, 2)
                else:
                    s.pwce(f'DRBD resource "{res_name}" does not exist', 3, 2)
        else:
            s.handle_exception()

    def _down(self, res_name):
        '''
        Stop the DRBD resource
        '''
        unique_str = 'UqmYgtM3'
        drbd_down_cmd = f'drbdadm down {res_name}'
        oprt_id = s.get_oprt_id()
        s.pwl(f'Start to down the DRBD resource "{res_name}"', 2, oprt_id, 'start')
        down_result = s.get_ssh_cmd(SSH, unique_str, drbd_down_cmd, oprt_id)
        if down_result:
            if down_result['sts']:
                s.pwl(f'Succeed in downing the DRBD resource "{res_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to down the DRBD resource"{res_name}"', 3, 2)
        else:
            s.handle_exception()

    def _del_config(self, res_name):
        '''
        remove the DRBD config file
        '''
        unique_str = 'UqkYgtM3'
        drbd_del_cmd = f'rm /etc/drbd.d/{res_name}.res'
        oprt_id = s.get_oprt_id()
        s.pwl(f'Start to delete the DRBD config file "{res_name}.res"', 2, oprt_id, 'start')
        del_result = s.get_ssh_cmd(SSH, unique_str, drbd_del_cmd, oprt_id)
        if del_result:
            if del_result['sts']:
                s.pwl(f'Succeed in deleting the DRBD config file "{res_name}.res"',3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to delete the DRBD config file "{res_name}.res"', 3, 2)
        else:
            s.handle_exception()

    def get_all_cfgd_drbd(self):
        # get list of all configured crm res
        cmd_drbd_status = 'drbdadm status'
        show_result = s.get_ssh_cmd(SSH, 'UikYgtM1', cmd_drbd_status, s.get_oprt_id())
        if show_result:
            if show_result['sts']:
                re_drbd = f'res_\w*_[0-9]{{1,3}}'
                show_result = show_result['rst'].decode('utf-8')
                drbd_cfgd_list = s.re_findall(re_drbd, show_result)
                return drbd_cfgd_list
            else:
                s.pwe(f'Failed to execute command "{cmd_drbd_status}"', 3, 2)
        else:
            s.handle_exception()

    def _del(self, res_name):
        s.pwl(f'Deleting DRBD resource {res_name}',1)
        if self._down(res_name):
            if self._del_config(res_name):
                return True

    def del_drbds(self, drbd_to_del_list):
        if drbd_to_del_list:
            s.pwl('Start to delete DRBD resource',0)
            for res_name in drbd_to_del_list:
                self._del(res_name)


class VplxCrm(object):
    def __init__(self):
        self.logger = consts.glo_log()
        self.rpl = consts.glo_rpl()
        self.id = consts.glo_id()
        self.str = consts.glo_str()
        if self.rpl == 'no':
            init_ssh()

    def cfg(self):
        time.sleep(0.5)
        lu_name = f'res_{self.str}_{self.id}'
        s.pwl('Start to configure crm resource', 1, '', 'start')
        self._create(lu_name)
        self._setting(lu_name)
        self._start(lu_name)
        time.sleep(0.5)
        self._status_verify(lu_name)
        return True

    def modify_initiator_and_verify(self):
        lu_name = f'res_{self.str}_{self.id}'
        self._modify_allow_initiator(lu_name)
        self._crm_and_targetcli_verify(lu_name)

    def _create(self, lu_name):
        '''
        Create iSCSILogicalUnit resource
        '''
        oprt_id = s.get_oprt_id()
        if consts.glo_iqn_list():
            initiator_iqn=' '.join(consts.glo_iqn_list())
        else:
            s.pwe('Global IQN list is None',2,2)
        unique_str = 'LXYV7dft'
        s.pwl(f'Start to create iSCSILogicalUnit resource "{lu_name}"', 2, oprt_id, 'start')
        drbd_dev_name = f'drbd{self.id}'
        cmd = f'crm conf primitive {lu_name} \
            iSCSILogicalUnit params target_iqn="{TARGET_IQN}" \
            implementation=lio-t lun={consts.glo_id()} path="/dev/{drbd_dev_name}"\
            allowed_initiators="{initiator_iqn}" op start timeout=600 interval=0 op stop timeout=600 interval=0 op monitor timeout=40 interval=50 meta target-role=Stopped'#40->600
        result = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result:
            if result['sts']:
                s.pwl(f'Succeed in creating iSCSILogicalUnit "{lu_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to create iSCSILogicalUnit "{lu_name}"', 3, 2)
        else:
            s.handle_exception()

    def _set_col(self, lu_name):
        '''
        Setting up iSCSILogicalUnit resources of colocation
        '''
        oprt_id = s.get_oprt_id()
        unique_str = 'E03YgRBd'
        cmd = f'crm conf colocation co_{lu_name} inf: {lu_name} {TARGET_NAME}'
        s.pwl(f'Start to set up colocation of iSCSILogicalUnit "{lu_name}"', 2, oprt_id, 'start')
        result_crm = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result_crm:
            if result_crm['sts']:
                s.pwl(f'Succeed in setting colocation of iSCSILogicalUnit "{lu_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to set colocation of iSCSILogicalUnit "{lu_name}"', 3, 2)
        else:
            s.handle_exception()

    def _set_order(self, lu_name):
        '''
        Setting up iSCSILogicalUnit resources of order
        '''
        oprt_id = s.get_oprt_id()
        unique_str = '0GHI63jX'
        cmd = f'crm conf order or_{lu_name} {TARGET_NAME} {lu_name}'
        s.pwl(f'Start to set up order of iSCSILogicalUnit "{lu_name}"', 2, oprt_id, 'start')
        result_crm = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result_crm:
            if result_crm['sts']:
                s.pwl(f'Succeed in setting order of iSCSILogicalUnit "{lu_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to set order of iSCSILogicalUnit "{lu_name}"', 3, 2)
        else:
            s.handle_exception()
    
    def _set_portblock(self, lu_name):
        oprt_id=s.get_oprt_id()
        unique_str='TgFqUiOkl'
        cmd=f'crm conf order or_{lu_name}_prtoff {lu_name} {PORTBLOCK_UNBLOCK_NAME}'
        s.pwl(f'Start to set up portblock of iSCSILogicalUnit "{lu_name}"', 2, oprt_id, 'start')
        results=s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if results:
            if results['sts']:
                s.pwl(f'Succeed in setting portblock of iSCSILogicalUnit "{lu_name}"', 3, oprt_id, 'finish')
                return True
            else:
                s.pwce(f'Failed to set portblock of iSCSILogicalUnit "{lu_name}"', 3, 2)
        else:
            s.handle_exception()

    def _setting(self, lu_name):
        if self._set_col(lu_name):
            if self._set_order(lu_name):
                if self._set_portblock(lu_name):
                    return True

    def _start(self, lu_name):
        '''
        start up the iSCSILogicalUnit resource
        '''
        oprt_id = s.get_oprt_id()
        unique_str = 'YnTDsuVX'
        cmd = f'crm res start {lu_name}'
        s.pwl(f'Start to start up the iSCSILogicalUnit "{lu_name}"', 2, oprt_id, 'start')
        result_cmd = s.get_ssh_cmd(SSH, unique_str, cmd, oprt_id)
        if result_cmd:
            if result_cmd['sts']:
                    s.pwl(f'Succeed in executing command to start up "{lu_name}".', 3, oprt_id, 'finish')
                    return True
            else:
                s.pwce(f'Failed to start up iSCSILogicaLUnit "{lu_name}"', 3, 2)
        else:
            s.handle_exception()
    
    def _status_verify(self, lu_name):
        oprt_id = s.get_oprt_id()
        s.pwl(f'Start to check the status of iSCSILogicalUnit "{lu_name}"', 2, oprt_id, 'start')
        if self._cyclic_check_crm_status(lu_name, 'Started',6,100):
            s.pwl(f'Succeed in starting up iSCSILogicaLUnit "{lu_name}"', 3, oprt_id, 'finish')
            return True
        else:
            s.pwce(f'Failed to start up iSCSILogicaLUnit "{lu_name}"', 3, 2)

    def _get_crm_status(self, res_name):
        '''
        Check the crm resource status
        '''
        unique_str = 'UqmUytK3'
        crm_show_cmd = f'crm res list | grep {res_name}'
        oprt_id = s.get_oprt_id()
        verify_result = s.get_ssh_cmd(SSH, unique_str, crm_show_cmd, oprt_id)
        if verify_result:
            if verify_result['sts']:
                re_string=f'''{res_name}\s*\(ocf::heartbeat:\w*\):\s*(\w*)'''
                re_result=s.re_search(re_string, verify_result['rst'].decode('utf-8'))
                if re_result:
                    return {'status': re_result.group(1)}
                else:
                    s.pwce(f'Failed to get status of CRM resource "{res_name}"',4,2)
            else:
                s.pwce('Failed to get status ofCRM resource "{res_name}"', 4, 2)
        else:
            s.handle_exception()

    def _cyclic_check_crm_status(self, res_name, expect_status,sec, num):
        '''
        Determine crm resource status is started/stopped
        '''
        n = 0
        while n < num:
            n += 1
            if self._get_crm_status(res_name)['status'] != expect_status:
                time.sleep(sec)
            else:
                return True

    def _stop(self, res_name):
        '''
        stop the iSCSILogicalUnit resource
        '''
        unique_str = 'UqmYgtM1'
        crm_stop_cmd = (f'crm res stop {res_name}')
        oprt_id = s.get_oprt_id()
        s.pwl(f'Start to stop iSCSILogicalUnit "{res_name}"', 2, oprt_id, 'start')
        crm_stop = s.get_ssh_cmd(SSH, unique_str, crm_stop_cmd, oprt_id)
        if crm_stop:
            if crm_stop['sts']:
                if self._cyclic_check_crm_status(res_name, 'Stopped',6,100):
                    s.pwl(f'Succeed in Stopping iSCSILogicalUnit "{res_name}"', 3, oprt_id, 'start')
                    return True
                else:
                    s.pwce(f'Failed to stop iSCSILogicalUnit "{res_name}"', 3, 2)
            else:
                s.pwce(f'Failed to stop iSCSILogicalUnit "{res_name}"', 3, 2)
        else:
            s.handle_exception()

    def _del_cof(self, res_name):
        '''
        Delete the iSCSILogicalUnit resource
        '''
        unique_str = 'EsTyUqIb5'
        crm_del_cmd = f'crm cof delete {res_name}'
        oprt_id = s.get_oprt_id()
        s.pwl(f'Start to delete iSCSILogicalUnit "{res_name}"', 2, oprt_id, 'start')
        del_result = s.get_ssh_cmd(SSH, unique_str, crm_del_cmd, oprt_id)
        # a:delete_result为error
        if del_result:
            re_delstr = 'deleted'
            re_result = s.re_findall(
                re_delstr, del_result['rst'].decode('utf-8'))
            if len(re_result)==3:
                s.pwl(f'Succeed in deleting iSCSILogicalUnit "{res_name}"', 3, oprt_id, 'start')
                return True
            else:
                s.pwce(f'Failed to delete iSCSILogicalUnit "{res_name}"', 3, 2)
        else:
            s.handle_exception()

    def _del(self, res_name):
        s.pwl(f'Deleting CRM resource {res_name}',1)
        if self._stop(res_name):
            if self._del_cof(res_name):
                return True

    def get_all_cfgd_res(self):
        # get list of all configured crm res
        cmd_crm_res_show = 'crm res show'
        show_result = s.get_ssh_cmd(
            SSH, 'IpJhGfVc4', cmd_crm_res_show, s.get_oprt_id())
        if show_result:
            if show_result['sts']:
                re_crm_res = f'res_\w*_[0-9]{{1,3}}'
                show_result = show_result['rst'].decode('utf-8')
                crm_res_cfgd_list = s.re_findall(re_crm_res, show_result)
                return crm_res_cfgd_list
        else:
            s.handle_exception()

    def del_crms(self, crm_to_del_list):
        if crm_to_del_list:
            s.pwl('Start to delete CRM resource',0)
            for res_name in crm_to_del_list:
                self._del(res_name)


    
    def _modify_allow_initiator(self, lu_name):
        s.pwl(f'Start to modify allowed initiator of "{lu_name}"', 2, '', 'start')
        iqn_string=' '.join(consts.glo_iqn_list())
        cmd=f'crm conf set {lu_name}.allowed_initiators "{iqn_string}"'
        oprt_id=s.get_oprt_id()
        result=s.get_ssh_cmd(SSH,'',cmd,oprt_id)
        if result:
            if result['sts']:
                s.pwl(f'Succeed in executing command to modify allow initiator.', 3, oprt_id, 'finish')
                return True
            else:
                s.pwe(f'Failed to modify the allowed initiator of "{lu_name}"', 3, 2)
        else:
            s.handle_exception()
    
    def _targetcli_verify(self):
        cmd=f'targetcli ls iscsi/{TARGET_IQN}/tpg1/acls'
        oprt_id=s.get_oprt_id()
        results=s.get_ssh_cmd(SSH,'',cmd,oprt_id)
        if results:
            if results['sts']:
                restr = re.compile(f'''(iqn.1993-08.org.debian:01:2b129695b8bbmaxhost:{self.id}-\d+).*?mapped_lun{self.id}''', re.DOTALL)
                re_result=restr.findall(results['rst'].decode('utf-8'))
                if re_result:
                    if re_result==consts.glo_iqn_list():
                        return True
        else:
            s.handle_exception()

    def _cyclic_check_crm_start(self, res_name, sec, num):
        n = 0
        while n < num:
            n += 1
            if self._get_crm_status(res_name)['status'] =='Stopped':
                time.sleep(sec)
            elif self._get_crm_status(res_name)['status']=='FAILED':
                s.pwe('Failed to start CRM resource, resource status become "FAILED"', 3, 2)
            else:
                if self._targetcli_verify():
                    return True
    
    def _crm_and_targetcli_verify(self, lu_name):
        oprt_id=s.get_oprt_id()
        s.pwl(f'Start to check status of CRM resource and targetcli', 2, '', 'start')
        if self._cyclic_check_crm_start(lu_name,6,200):
            s.pwl(f'Success in modifying the allowed initiator of "{lu_name}"', 3, oprt_id,'finish')
        else:
            s.pwe(f'Failed to modify the allowed initiator of "{lu_name}"', 3, 2)
        

if __name__ == '__main__':
   pass
