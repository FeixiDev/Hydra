import sundry
import consts

def test_generate_iqn():
	sundry.generate_iqn(100)
	assert consts._GLOBAL_DICT['IQN_LIST'] == ['iqn.1993-08.org.debian:01:2b129695b8bbmaxhost100']

class TestDebugLog:
	
	def setup_class(self):
		self.debug = sundry.DebugLog()

	def test_mk_debug_folder(self):
		assert self.debug._mk_debug_folder() == None

	def test_prepare_debug_log(self):
		assert self.debug.prepare_debug_log() == None

	def test_get_debug_log(self):
		pass
		