# Copyright (C) 2007 Lemur Consulting Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""Start flax as Windows Service.

"""
__docformat__ = "restructuredtext en"

import setuppaths
import servicemanager
import win32api
import win32con
import win32service
import win32serviceutil
import win32event
import win32evtlogutil

import os
import sys

from servicemanager import LogInfoMsg, LogErrorMsg

# Get any Registry settings
from flax_w32 import FlaxRegistry
_reg = FlaxRegistry()



import startflax
import multiprocessing

# once the service is created it'll need permissions to write the log
# files.  Either change the permissions on the log files, or change
# the user that the service runs as to one that can write the log files.

# Also it'll need permissions to read all the document
# collections. This can particularly be an issue with network
# drives. Again - either change the permissions or the user that the
# service runs as.

#need to patch multiprocessing - see http://bugs.python.org/issue5162




import flaxpaths

class FlaxService(win32serviceutil.ServiceFramework):

    _svc_name_ = "FlaxService"
    _svc_display_name_ = "Flax Service"
    _svc_deps_ = ["EventLog"]

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        servicemanager.SetEventSourceName(self._svc_display_name_)

        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        LogInfoMsg('The Flax service is initialising.')

        try:
            # Set options according to our configuration, and create the class
            # which manages starting and stopping the flax threads and processes.
            self._options = startflax.StartupOptions(main_dir = _reg.runtimepath,
                                                    src_dir = _reg.runtimepath,
                                                    dbs_dir = _reg.datapath)
            self._flax_main = startflax.FlaxMain(self._options)
            LogInfoMsg('The Flax service is initialised.')
        except:
            import traceback
            tb=traceback.format_exc()
            LogErrorMsg('Exception during initialisation, traceback follows:\n %s' % tb)            
          

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        # This call to stop() may take some time, but this shouldn't cause
        # windows to complain because the SvcDoRun thread will have awoken and
        # be sending SERVICE_STOP_PENDING messages every 4 seconds until join()
        # returns True.
        try:
            self._flax_main.stop()
        except:
            import traceback
            tb=traceback.format_exc()
            LogErrorMsg('Exception during SvcStop, traceback follows:\n %s' % tb)            

    def SvcDoRun(self):
        # Write a 'started' event to the event log...
        LogInfoMsg('The Flax service has started.')

        # Redirect stdout and stderr to avoid buffer overflows and to allow
        # debugging while acting as a service
        sys.stderr = open(os.path.join(flaxpaths.paths.log_dir, 'flax_stderr.log'), 'w')
        sys.stdout = open(os.path.join(flaxpaths.paths.log_dir, 'flax_stdout.log'), 'w')

        try:
            # Start flax, non-blocking.
            self._flax_main.start(blocking = False)
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            # Wait for message telling us that we're stopping.
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            LogInfoMsg('The Flax service is stopping.')
            # Wait for the service to stop (and reassure windows that we're still
            # trying to stop).
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, 5000)
            while not self._flax_main.join(4):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, 5000)

            # Perform cleanup.
            # This is needed because of a bug in PythonService.exe - it doesn't
            # call Py_Finalize(), so atexit handlers don't get called.  We call
            # sys.exit_func() directly as a workaround.  When the
            # bug is fixed, we should stop doing this.  See:
            # https://sourceforge.net/tracker/?func=detail&atid=551954&aid=1273738&group_id=78018
            # for details.
            sys.exitfunc()

            sys.stderr.close()
            sys.stdout.close()
            
            # Log that we've stopped.
            LogInfoMsg('The Flax service has stopped.')

            # The python service framework will tell windows that we've stopped
            # when we return from this function, so we don't need to do that
            # explicitly.
        except:
            import traceback
            tb=traceback.format_exc()
            LogErrorMsg('Exception during SvcDoRun, traceback follows:\n %s' % tb)            

        
def ctrlHandler(ctrlType):
    """A windows control message handler.

    This is needed to prevent the service exiting when the user who started it
    exits.

    FIXME - we should probably handle ctrlType = CTRL_SHUTDOWN_EVENT
    differently.

    """
    return True

# Note that this method is never run in the 'frozen' executable, however it may be used for debugging
if __name__ == '__main__':
    multiprocessing.freeze_support()
    win32api.SetConsoleCtrlHandler(ctrlHandler, True)
    win32serviceutil.HandleCommandLine(FlaxService)
