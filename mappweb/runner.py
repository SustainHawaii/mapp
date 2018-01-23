import os
import sys
import subprocess
from mappweb.guitest_settings import SERVER_ADDR
from django_nose import NoseTestSuiteRunner
import mongoengine as mongo


class LiveServerTestRunner(NoseTestSuiteRunner):

    def _spawn_server(self):
        """Return whether the ``SPAWN_GUI_SERVER`` flag was passed"""
        return os.getenv('SPAWN_GUI_SERVER', 'true') in ('true', '1')

    def setup_databases(self, **kwargs):
        retval = super(LiveServerTestRunner, self).setup_databases(**kwargs)
        if self._spawn_server():
            self.spawn_server()
        mongo.connection.connect('test_Maps', 'test')
        mongo.connection.disconnect('default')
        self.conn = mongo.connect('test')

        return retval

    def spawn_server(self):
        gui_settings = 'mappweb.guitest_settings'
        server_command = ["./manage.py", "runserver",
                          SERVER_ADDR, "--settings=" + gui_settings]
        self.server_p = subprocess.Popen(
            server_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            preexec_fn=os.setsid
        )
        print("server process started up... continuing with test execution")

    def kill_server(self):
        try:
            print("killing server process...")
            os.killpg(os.getpgid(self.server_p.pid), 15)
            self.server_p.wait()
        except:
            print("exception", sys.exc_info()[0])

    def teardown_databases(self, old_config, **kwargs):
        if self._spawn_server():
            self.kill_server()
        self.conn.drop_database('test')
        return super(LiveServerTestRunner, self).teardown_databases(
            old_config, **kwargs)
