import main


class TestHydraArgParse:

	def setup_class(self):
		self.hydra = main.HydraArgParse()

	# def test_log_user_input(self):
	# 	assert self.hydra.log_user_input() == None

	# def test_argparse_init(self):
	# 	assert self.hydra.argparse_init() == None

	# def test_storage(self):
	# 	assert self.hydra._storage() == None

	# def test_vplx_drbd(self):
	# 	assert self.hydra._vplx_drbd() == None

	# def test_vplx_crm(self):
	# 	assert self.hydra._vplx_crm() == None

	# def test_host_test(self):
	# 	assert self.hydra._host_test() == None


	def test_start(self):
		self.hydra.start()