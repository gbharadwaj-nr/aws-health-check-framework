"""
===========================================================
AWS Daily Health Check Framework
Production Version
===========================================================
"""

import os
import sys
from datetime import datetime

from config import CLIENTS
from auth import assume_role
from region_discovery import discover_regions

from checks.ec2 import check_ec2
from checks.rds import check_rds
from checks.asg import check_asg
from checks.cloudwatch import check_cloudwatch
from checks.lambda_health import check_lambda

from reports.report_utils import create_output_folder
from reports.html_report import generate_html_report


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
# Jenkins Client Mapping
# ---------------------------------------------------------

def get_account(client):

    aliases = {
        "ATB":"ATB",
        "BOQ":"Bank of Queensland (BoQ)",
        "BHFS":"BHFS",
        "COOP":"Coop",
        "EQUIFAX":"Equifax",
        "FLEETCOR":"FleetCor",
        "GENERALI":"Generali",
        "IAG":"IAG",
        "LFS":"Latitude (LFS)",
        "MGL":"Macquarie (MGL)",
        "MIZUHO":"Mizuho",
        "NBS":"NationWide (NBS)",
        "SUNCORP":"Suncorp",
        "TABCORP":"TabCorp"
    }

    client = aliases.get(client.upper(), client)

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
        print("-" * 50)
        print(f"Selected Client : {selected_client}")

        account = get_account(selected_client)

        if account is None:
            print("Invalid CLIENT Parameter")
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

    print("\nDiscovering Active Regions...\n")

    regions = discover_regions(session)

    if not regions:
        print("No AWS Resources Found")
        sys.exit(0)

    for region in regions:
        print(f"[OK] {region}")

    print(f"\nTotal Active Regions : {len(regions)}")

    # ---------------------------------------------------------
    # Create Output Folder
    # ---------------------------------------------------------

    output_folder = create_output_folder(account["client_name"])

    print("\nOutput Folder")
    print("-" * 50)
    print(output_folder)

    # ---------------------------------------------------------
    # Run Health Checks
    # ---------------------------------------------------------

    print("\nRunning EC2 Health Check...")
    ec2_data = check_ec2(session, regions)

    print("Running RDS Health Check...")
    rds_data = check_rds(session, regions)

    print("Running Auto Scaling Health Check...")
    asg_data = check_asg(session, regions)

    print("Running CloudWatch Alarm Check...")
    cloudwatch_data = check_cloudwatch(session, regions)

    print("Running Lambda Health Check...")
    lambda_data = check_lambda(session, regions)

    # ---------------------------------------------------------
    # Build Report Object
    # ---------------------------------------------------------

    report_data = {

        "generated_time": datetime.now(),

        "client": account,

        "regions": regions,

        "ec2": ec2_data,

        "rds": rds_data,

        "asg": asg_data,

        "cloudwatch": cloudwatch_data,

        "lambda": lambda_data

    }

    # ---------------------------------------------------------
    # Console Summary
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)

    print(f"EC2 Running           : {ec2_data['running']}")
    print(f"EC2 Total             : {ec2_data['total']}")

    print(f"RDS Available         : {rds_data['available']}")
    print(f"RDS Total             : {rds_data['total']}")

    print(f"Healthy ASGs          : {asg_data['healthy']}")
    print(f"Total ASGs            : {asg_data['total']}")

    print(f"CloudWatch Alarms     : {cloudwatch_data['alarm_count']}")

    print(f"Healthy Lambda        : {lambda_data['healthy']}")
    print(f"Total Lambda          : {lambda_data['total']}")

    generate_html_report(

    output_folder,

    account,

    ec2_data,

    rds_data,

    asg_data,

    cloudwatch_data,

    lambda_data

)

    print("\nFramework Initialization Completed Successfully.")

    # ---------------------------------------------------------
    # HTML Report (Next Step)
    # ---------------------------------------------------------

    # generate_html_report(report_data, output_folder)


if __name__ == "__main__":
    main()