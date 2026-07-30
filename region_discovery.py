"""
===========================================================
Region Discovery
===========================================================
"""

import boto3


def discover_regions(session):

    ec2 = session.client("ec2", region_name="us-east-1")

    all_regions = ec2.describe_regions()["Regions"]

    active_regions = []

    for region in all_regions:

        region_name = region["RegionName"]

        client = session.client("ec2", region_name=region_name)

        try:

            response = client.describe_instances()

            reservations = response["Reservations"]

            if len(reservations) > 0:
                active_regions.append(region_name)

        except Exception:
            pass

    return active_regions