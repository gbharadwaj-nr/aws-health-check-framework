"""
===========================================================
RDS Health Check Module
===========================================================
"""

from botocore.exceptions import ClientError


def check_rds(session, regions):

    rds_list = []

    available = 0
    unavailable = 0

    for region in regions:

        try:

            rds = session.client("rds", region_name=region)

            response = rds.describe_db_instances()

        except ClientError as e:

            print(f"Unable to query RDS in {region}: {e}")

            continue

        for db in response["DBInstances"]:

            status = db["DBInstanceStatus"]

            if status == "available":
                available += 1
            else:
                unavailable += 1

            rds_list.append({

                "region": region,

                "db_identifier": db["DBInstanceIdentifier"],

                "engine": db["Engine"],

                "status": status,

                "multi_az": db["MultiAZ"],

                "allocated_storage": db["AllocatedStorage"],

                "instance_class": db["DBInstanceClass"]

            })

    return {

        "available": available,

        "unavailable": unavailable,

        "total": available + unavailable,

        "databases": rds_list

    }