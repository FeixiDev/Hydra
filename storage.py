#  coding: utf-8
import connect
import sundry as s
import consts

HOST = '10.203.1.231'
PORT = 23
USERNSME = 'root'
PASSWORD = 'Feixi@123'
TIMEOUT = 3
TELNET_CONN = None


def init_telnet():
    global TELNET_CONN
    if not TELNET_CONN:
        TELNET_CONN = connect.ConnTelnet(
            HOST, PORT, USERNSME, PASSWORD, TIMEOUT)
    else:
        pass


class DebugLog(object):
    def __init__(self):
        init_telnet()

    def get_storage_debug(self, debug_folder):
        cmd_debug = consts.get_cmd_debug_stor()
        for cmd in cmd_debug:
            result = TELNET_CONN.execute_command(cmd)
            with open(f'{debug_folder}/Storage_{HOST}.log', 'a') as f:
                f.write(result)


class Storage:
    '''
    Create LUN and map to VersaPLX
    '''

    def __init__(self):
        self.rpl = consts.glo_rpl()
        self.TID = consts.glo_tsc_id()
        self.logger = consts.glo_log()
        if self.rpl == 'no':
            init_telnet()

    def lun_create_map(self):
        s.pwl('Start to configure LUN on NetApp Storage', 0, s.get_oprt_id(), 'start')
        self._info()
        self._lun_create()
        self._lun_map()

    def _info(self):
        self.ID = consts.glo_id()
        self.STR = consts.glo_str()
        self.lun_name = f'{self.STR}_{self.ID}'



    def _lun_create(self):
        '''
        Create LUN with 10M bytes in size
        '''
        oprt_id = s.get_oprt_id()
        unique_str = 'jMPFwXy2'
        cmd = f'lun create -s 10m -t linux /vol/esxi/{self.lun_name}'
        info_msg = f'Start to create LUN, LUN name: "{self.lun_name}",LUN ID: "{self.ID}"'
        s.pwl(f'{info_msg}', 2, oprt_id, 'start')
        result = s.ex_telnet_cmd(TELNET_CONN, unique_str, cmd, oprt_id)
        if result:
            s.pwl(f'Succeed in creating LUN "{self.lun_name}"', 3, oprt_id, 'finish')
        else:
            s.handle_exception()

    def _lun_map(self):
        '''
        Map lun of specified lun_id to initiator group
        '''
        oprt_id = s.get_oprt_id()
        unique_str = '1lvpO6N5'
        info_msg = f'Start to map LUN, LUN name: "{self.lun_name}", LUN ID: "{self.ID}"'
        cmd = f'lun map /vol/esxi/{self.lun_name} hydra {self.ID}'
        s.pwl(f'{info_msg}', 2, oprt_id, 'start')
        result = s.ex_telnet_cmd(TELNET_CONN, unique_str, cmd, oprt_id)
        if result:
            re_string=f'LUN /vol/esxi/{self.lun_name} was mapped to initiator group hydra={self.ID}'
            re_result=s.re_search(re_string, result)
            if re_result:
                s.pwl(f'Finish mapping LUN "{self.lun_name}" to VersaPLX', 3, oprt_id, 'finish')
            else:
                s.pwce(f'Failed to map LUN "{self.lun_name}"', 3, 2)
        else:
            s.handle_exception()

    def _lun_unmap(self, lun_name):
        '''
        Unmap LUN and determine its succeed
        '''
        unique_str = '2ltpi6N5'
        oprt_id = s.get_oprt_id()
        unmap = f'lun unmap /vol/esxi/{lun_name} hydra'
        unmap_result = s.ex_telnet_cmd(TELNET_CONN, unique_str, unmap, oprt_id)
        if unmap_result:
            unmap_re = r'unmapped from initiator group hydra'
            re_result = s.re_search(unmap_re, unmap_result)
            if re_result:
                s.pwl(f'Unmap the lun /vol/esxi/{lun_name}  successfully',2)
                return True
            else:
                # -m:只有在出错之后才打印和记录,不过不退出.正常完成的不记录
                s.pwe(f'Can not unmap lun {lun_name}',2,1)
                # print(f'can not unmap lun {lun_name}')
        else:
            print('Unmap command execute failed')

    def _lun_destroy(self, lun_name):
        '''
        delete LUN and determine its succeed
        '''
        unique_str = '2ltpi6N3'
        oprt_id = s.get_oprt_id()
        destroy_cmd = f'lun destroy /vol/esxi/{lun_name}'
        destroy_result = s.ex_telnet_cmd(TELNET_CONN, unique_str, destroy_cmd, oprt_id)
        if destroy_result:
            re_destroy = f'LUN /vol/esxi/{lun_name} destroyed'
            re_result = s.re_search(re_destroy, destroy_result)
            if re_result:
                s.pwl(f'Destroy the lun /vol/esxi/{lun_name} successfully',2)
                return True
            else:
                s.pwe(f'Can not destroy lun {lun_name}',2,1)
        else:
            print('Destroy command execute failed')

    def get_all_cfgd_lun(self):
        # get list of all configured luns
        cmd_lun_show = 'lun show'
        show_result = s.ex_telnet_cmd(TELNET_CONN,
            '2lYpiKm3', cmd_lun_show, s.get_oprt_id())
        if show_result:
            re_lun = f'/vol/esxi/(\w*_[0-9]{{1,3}})'
            lun_cfgd_list = s.re_findall(re_lun, show_result)
            return lun_cfgd_list

    def del_luns(self, lun_to_del_list):
        s.pwl('Start to delete storage LUN', 0, '', 'delete')
        for lun_name in lun_to_del_list:
            s.pwl(f'Deleting LUN "{lun_name}"', 1, '', 'delete')
            self._lun_unmap(lun_name)
            self._lun_destroy(lun_name)


if __name__ == '__main__':
    pass
    # test_stor = Storage('31', 'luntest')
    # test_stor.lun_create()
    # test_stor.lun_map()
    # test_stor.TELNET_CONN.close()
