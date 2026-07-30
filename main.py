"""
===========================================================
AWS Daily Health Check Framework
===========================================================
"""

import os
import sys

from config import CLIENTS
from auth import assume_role
from region_discovery import discover_regions

# Import Health Check Modules
from checks.ec2 import check_ec2


# ---------------------------------------------------------
# Display Menu
# ---------------------------------------------------------

def show_menu():

    print("\n" + "=" * 90)
    print("AWS DAILY HEALTH CHECK FRAMEWORK")
    print("=" * 90)

    print(f"{'No':<5}{'Client Name':<35}{'Business Region'}")
    print("-" * 90)

    for key, value in CLIENTS.items():
        print(f"{key:<5}{value['client_name']:<35}{value['business_region']}")

    choice = input("\nSelect Client : ").strip()

    if choice not in CLIENTS:
        print("Invalid Selection")
        sys.exit(1)

    return CLIENTS[choice]


# ---------------------------------------------------------
# Jenkins Support
# ---------------------------------------------------------

def get_account(client):

    aliases = {
        "ATB": "ATB",
        "BOQ": "Bank of Queensland (BoQ)",
        "BHFS": "BHFS",
        "COOP": "Coop",
        "EQUIFAX": "Equifax",
        "FLEETCOR": "FleetCor",
        "GENERALI": "Generali",
        "IAG": "IAG",
        "LFS": "Latitude (LFS)",
        "MGL": "Macquarie (MGL)",
        "MIZUHO": "Mizuho",
        "NBS": "NationWide (NBS)",
        "SUNCORP": "Suncorp",
        "TABCORP": "TabCorp"
    }

    if client.upper() in aliases:
        client = aliases[client.upper()]

    for account in CLIENTS.values():
        if account["client_name"] == client:
            return account

    return None


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    selected_client = os.getenv("CLIENT")

    if selected_client:

        print("\nRunning from Jenkins")
        print("---------------------------------------")
        print(f"Selected Client : {selected_client}")

        account = get_account(selected_client)

        if account is None:
            print("Invalid CLIENT parameter")
            sys.exit(1)

    else:

        account = show_menu()

    print("\nSelected Account")
    print("-" * 50)

    print(f"Client Name      : {account['client_name']}")
    print(f"Business Region  : {account['business_region']}")
    print(f"AWS Account ID   : {account['account_id']}")

    print("\nAssuming Role...")

    session = assume_role(account)

    print("SUCCESS")

    print("\nDiscovering Active AWS Regions...\n")

    regions = discover_regions(session)

    if not regions:

        print("No AWS resources found.")
        sys.exit(0)

    for region in regions:
        print(f"[OK] {region}")

    print(f"\nTotal Active Regions : {len(regions)}")

    # ==========================================================
    # EC2 HEALTH CHECK
    # ==========================================================

    ec2_data = check_ec2(session, regions)

    print("\n" + "=" * 70)
    print("EC2 SUMMARY")
    print("=" * 70)

    print(f"Running Instances : {ec2_data['running']}")
    print(f"Stopped Instances : {ec2_data['stopped']}")
    print(f"Total Instances   : {ec2_data['total']}")

    print("\nFramework Initialization Completed Successfully.")


if __name__ == "__main__":
    main()