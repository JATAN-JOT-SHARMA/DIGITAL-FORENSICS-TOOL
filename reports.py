import json
from pathlib import Path

class ReportGenerator:

    def __init__(self, data, logger):
        self.data = data
        self.log = logger

    def generate(self):

        output = Path("output")
        output.mkdir(exist_ok=True)

        file = output / "forensic_report.json"

        with open(file, "w") as f:
            json.dump(
                self.data,
                f,
                indent=4
            )

        self.log(
            f"Report saved: {file}"
        )
