import json
import os
from datetime import datetime

def share_with_hr(report_data):
    """
    Simulates sending reports to HR by saving a nicely formatted
    JSON file locally. In production, this can be swapped with
    an SMTP email function or database push.
    """
    os.makedirs("hr_reports", exist_ok=True)
    filename = f"hr_reports/Candidate_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=4)

    return filename
