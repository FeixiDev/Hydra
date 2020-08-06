# coding:utf-8
import consts
import sys
import log
import sundry as s

sys.path.append('../')
consts._init()

transaction_id = s.get_transaction_id()
logger = log.Log(transaction_id)
consts.set_glo_log(logger)
consts.set_glo_tsc_id(transaction_id)
consts.set_glo_id(99)
consts.set_glo_str('pytest')