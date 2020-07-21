#  coding: utf-8
import connect
import time
import sundry as s
import logdb
import consts
import re
import subprocess

# global _TID

host = '10.203.1.231'
port = 23
username = 'root'
password = 'Feixi@123'
timeout = 3


class DebugLog(object):
    def __init__(self):
        self.telnet_conn = connect.ConnTelnet(
            host, port, username, password, timeout)

    def get_storage_debug(self, debug_folder):
        cmd_debug = consts.get_cmd_debug_stor()
        for cmd in cmd_debug:
            result = self.telnet_conn.execute_command(cmd)
            with open(f'{debug_folder}/Storage_{host}.log', 'a') as f:
                f.write(result)


class Storage:
    '''
    Create LUN and map to VersaPLX
    '''

    def __init__(self):
        self.logger = consts.glo_log()
        self.ID = consts.glo_id()
        self.STR = consts.glo_str()
        self.ID_LIST = consts.glo_id_list()
        self.rpl = consts.glo_rpl()
        self.TID = consts.glo_tsc_id()
        self.lun_name = f'{self.STR}_{self.ID}'
        if self.rpl == 'no':
            self.telnet_conn = connect.ConnTelnet(
                host, port, username, password, timeout)
        # print('Connect to storage NetApp')

    def ex_telnet_cmd(self, unique_str, cmd, oprt_id):
        if self.rpl == 'no':
            self.logger.write_to_log(
                'F', 'DATA', 'STR', unique_str, '', oprt_id)
            self.logger.write_to_log(
                'T', 'OPRT', 'cmd', 'telnet', oprt_id, cmd)
            result = self.telnet_conn.execute_command(cmd)
            #-m:log DATA telnet 
            logger.write_to_log(result)
            return result

        elif self.rpl == 'yes':
            db = consts.glo_db()
            db_id, oprt_id = db.find_oprt_id_via_string(self.TID, unique_str)
            # info_start = db.get_info_start(oprt_id)
            # if info_start:
            #     print(info_start)
            # info_end = db.get_info_finish(oprt_id)
            # if info_end:
            #     print(info_end)
            s.change_pointer(db_id)
            # print(f'  Change DB ID to: {db_id}')
            return True

    def lun_create(self):
        '''
        Create LUN with 10M bytes in size
        '''
        oprt_id = s.get_oprt_id()
        unique_str = 'jMPFwXy2'
        cmd = f'lun create -s 10m -t linux /vol/esxi/{self.lun_name}'
        info_msg = f'Start to create LUN, LUN name: {self.lun_name}, LUN ID: {self.ID}'
        s.pwl(f'{info_msg}', 2, oprt_id, 'start')
        # print(f'  Start to {info_msg}')# 正常打印
        # self.logger.write_to_log(
        #     'T', 'INFO', 'info', 'start', oprt_id, f'  Start to {info_msg}')
        self.ex_telnet_cmd(unique_str, cmd, oprt_id)
        s.pwl(f'Succeed in creating LUN {self.lun_name}', 2, oprt_id, 'finish')

    def lun_map(self):
        '''
        Map lun of specified lun_id to initiator group
        '''
        oprt_id = s.get_oprt_id()
        unique_str = '1lvpO6N5'
        info_msg = f'Start to map LUN, LUN name: {self.lun_name}, LUN ID: {self.ID}' #-v + Start to
        cmd = f'lun map /vol/esxi/{self.lun_name} hydra {self.ID}'
        # print(f'  Start to {info_msg}')
        # self.logger.write_to_log(
        #     'T', 'INFO', 'info', 'start', oprt_id, f'  Start to {info_msg}')

        s.pwl(f'{info_msg}',2,oprt_id,'start') #-v 删除空格、Start to
        self.ex_telnet_cmd(unique_str, cmd, oprt_id)
        # print(f'  Finish with {info_msg}')
        # self.logger.write_to_log(
        #     'T', 'INFO', 'info', 'finish', oprt_id, f'  Finish with {info_msg}')
        s.pwl(f'Finish mapping LUN {self.lun_name} to VersaPLX', 2, oprt_id, 'finish')

    def lun_create_verify(self):
        pass

    def lun_map_verify(self):
        pass

    def lun_unmap(self, lun_name):
        '''
        Unmap LUN and determine its succeed
        '''
        unique_str = '2ltpi6N5'
        oprt_id = s.get_oprt_id()
        unmap = f'lun unmap /vol/esxi/{lun_name} hydra'
        unmap_result = self.ex_telnet_cmd(unique_str, unmap, oprt_id)
        if unmap_result:
            unmap_re = r'unmapped from initiator group hydra'
            re_result = s.re_findall(unmap_re, unmap_result)
            if re_result:
                # print(f'/vol/esxi/{lun_name} unmap succeed')
                return True
            else:
                #-m:只有在出错之后才打印和记录,不过不退出.正常完成的不记录
                s.prt(f'can not unmap lun {lun_name}')
                # print(f'can not unmap lun {lun_name}')
        else:
            print('unmap command execute failed')

    def lun_destroy(self, lun_name):
        '''
        delete LUN and determine its succeed
        '''
        unique_str = '2ltpi6N3'
        oprt_id = s.get_oprt_id()
        destroy_cmd = f'lun destroy /vol/esxi/{lun_name}'
        destroy_result = self.ex_telnet_cmd(unique_str, destroy_cmd, oprt_id)
        if destroy_result:
            re_destroy = r'destroyed'
            re_result = s.re_findall(re_destroy, destroy_result)
            if re_result:
                # print(f'/vol/esxi/{lun_name} destroy succeed')
                return True
            else:
                print(f'can not destroy LUN {lun_name}')
        else:
            print('destroy command execute failed')

    def get_all_cfgd_lun(self):
        # get list of all configured luns
        cmd_lun_show = 'lun show'
        show_result = self.ex_telnet_cmd(
            '2lYpiKm3', cmd_lun_show, s.get_oprt_id())
        if show_result:
            re_lun = f'/vol/esxi/(\w*_[0-9]{{1,3}})'
            lun_cfgd_list = s.re_findall(re_lun, show_result)
            return lun_cfgd_list

    # def get_and_show_lun_to_del(self):
    #     '''
    #     Get all luns through regular matching
    #     '''
    #     # get list of all configured luns
    #     lun_cfgd_list = self._get_all_cfgd_lun()
    #     lun_to_del_list = s.get_to_del_list(lun_cfgd_list)
    #     s.prt_res_to_del(lun_to_del_list)
    #     return lun_to_del_list

    def del_all(self, lun_to_del_list):
        for lun_name in lun_to_del_list:
            s.pwl(f'Deleting LUN "{lun_name}"')
            self.lun_unmap(lun_name)
            self.lun_destroy(lun_name)


if __name__ == '__main__':
    pass
    # test_stor = Storage('31', 'luntest')
    # test_stor.lun_create()
    # test_stor.lun_map()
    # test_stor.telnet_conn.close()
