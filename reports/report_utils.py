"""
Utility functions for report generation
"""

import os
from datetime import datetime


def create_output_folder(client_name):
    """
    Creates output folder like

    output/
        BHFS/
            2026-07-31/

    Returns full folder path.
    """

    today = datetime.now().strftime("%Y-%m-%d")

    folder = os.path.join(
        "output",
        client_name,
        today
    )

    os.makedirs(folder, exist_ok=True)

    return folder