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
from checks.rds import check_rds
from checks.asg import check_asg
from checks.cloudwatch import check_cloudwatch
from Checks.lambda_health import check_lambda  


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

    rds_data = check_rds(session, regions)

    print("\n" + "=" * 70)
    print("RDS SUMMARY")
    print("=" * 70)

    print(f"Available Databases : {rds_data['available']}")
    print(f"Unavailable         : {rds_data['unavailable']}")
    print(f"Total Databases     : {rds_data['total']}")

    asg_data = check_asg(session, regions)

    print("\n")
    print("=" * 70)
    print("AUTO SCALING GROUP SUMMARY")
    print("=" * 70)

    if asg_data["total"] == 0:

        print("No Auto Scaling Groups Found")

    else:

        print(f"Healthy ASGs   : {asg_data['healthy']}")
        print(f"Unhealthy ASGs : {asg_data['unhealthy']}")
        print(f"Total ASGs     : {asg_data['total']}")

        print("\nDetails")
        print("-" * 70)

        for group in asg_data["groups"]:

            print(
                f"{group['region']:15}"
                f"{group['asg_name']:35}"
                f"Desired={group['desired']} "
                f"Current={group['current']} "
                f"Healthy={group['healthy']} "
                f"Status={group['status']}"
            )
    cloudwatch_data = check_cloudwatch(session, regions)

    print("\n")
    print("=" * 70)
    print("CLOUDWATCH ALARMS")
    print("=" * 70)

    if cloudwatch_data["alarm_count"] == 0:

        print("No CloudWatch Alarms in ALARM state")

    else:

        print(f"Active Alarms : {cloudwatch_data['alarm_count']}")

        print("\nAlarm Details")
        print("-" * 120)

        print(
            f"{'Region':15}"
            f"{'Alarm Name':40}"
            f"{'Metric':25}"
            f"{'State':10}"
        )

        print("-" * 120)

        for alarm in cloudwatch_data["alarms"]:

            print(
                f"{alarm['region']:15}"
                f"{alarm['alarm_name'][:38]:40}"
                f"{alarm['metric'][:23]:25}"
                f"{alarm['state']:10}"
            )

            print(f"{'':15}Reason : {alarm['reason']}")
            
    lambda_data = check_lambda(session, regions)

    print("\n")
    print("=" * 70)
    print("LAMBDA HEALTH")
    print("=" * 70)

    if lambda_data["total"] == 0:

        print("No Production Lambda Functions Found")

    else:

        print(f"Healthy Functions   : {lambda_data['healthy']}")
        print(f"Unhealthy Functions : {lambda_data['unhealthy']}")
        print(f"Total Functions     : {lambda_data['total']}")

        print("\nDetails")
        print("-" * 130)

        print(
            f"{'Region':15}"
            f"{'Function Name':45}"
            f"{'Runtime':15}"
            f"{'Errors':10}"
            f"{'Status':12}"
        )

        print("-" * 130)

        for function in lambda_data["functions"]:

            print(
                f"{function['region']:15}"
                f"{function['name'][:43]:45}"
                f"{function['runtime']:15}"
                f"{function['errors']:<10}"
                f"{function['status']:12}"
            )

            print(
                f"{'':15}"
                f"Memory={function['memory']}MB  "
                f"Timeout={function['timeout']}s  "
                f"State={function['state']}"
            )
if __name__ == "__main__":
    main()