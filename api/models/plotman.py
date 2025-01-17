import os
import re
import traceback

from api import app

PID_FILE = '/root/.chia/plotman/plotman.pid'

class PlottingSummary:

    def __init__(self, cli_stdout, plotman_pid):
        self.rows = []
        for line in cli_stdout:
            if not line.strip() or line.startswith("Total jobs") or line.startswith("Updated at") or line.startswith("Jobs in"):
                pass
            elif "plot id" in line.strip(): # The header row
                self.columns = line.replace('plot id', 'plot_id').strip().split()
                # Plotman has two columns both named 'tmp' so change the 2nd one to 'size'
                self.columns[7] = 'size'
            elif re.match(r'^(\w){8}\s.*$', line.strip()): # A regular plotting row, so create as dictionary
                row = {}
                values = line.split()
                i = 0
                for i in range(len(self.columns)):
                    row[self.columns[i]] = values[i]
                    i += 1
                self.rows.append(row)
            elif re.match(r'^(\w){7}\s.*$', line.strip()): # A bladebit plotting row with no 'tmp' value col
                row = {}
                values = line.split()
                values.insert(3, '-')  # For tmp dir location, bladebit doesn't use it.
                app.logger.info(values)
                i = 0
                for i in range(len(self.columns)):
                    row[self.columns[i]] = values[i]
                    i += 1
                self.rows.append(row)
            else:
                app.logger.info("Unkown Plotman status line: {0}".format(line))
        self.calc_status()
        if plotman_pid:
            self.plotman_running = True
        else:
            self.plotman_running = False

    def calc_status(self):
        if len(self.rows) > 0:
            self.display_status = "Active"
        else:
            self.display_status = "Idle"       
