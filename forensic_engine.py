import platform
import datetime


class ForensicEngine:

    def __init__(self, logger):
        self.log = logger

    def run_full(self):

        self.log("Collecting forensic evidence...")

        return {
            "system": platform.system(),
            "machine": platform.machine(),
            "time": str(datetime.datetime.now())
        }