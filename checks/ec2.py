"""
===========================================================
EC2 Health Check Module
===========================================================
"""

from botocore.exceptions import ClientError


def check_ec2(session, regions):
    """
    Collect EC2 Inventory and Health Status

    Returns:
    {
        "running": int,
        "stopped": int,
        "total": int,
        "instances": []
    }
    """

    running = 0
    stopped = 0

    instance_list = []

    for region in regions:

        ec2 = session.client("ec2", region_name=region)

        try:
            reservations = ec2.describe_instances()["Reservations"]

        except ClientError as e:
            print(f"Unable to query EC2 in {region}: {e}")
            continue

        # -----------------------------------------
        # Instance Status Lookup
        # -----------------------------------------

        status_lookup = {}

        try:

            statuses = ec2.describe_instance_status(
                IncludeAllInstances=True
            )["InstanceStatuses"]

            for status in statuses:

                status_lookup[status["InstanceId"]] = {

                    "system_status":
                        status["SystemStatus"]["Status"],

                    "instance_status":
                        status["InstanceStatus"]["Status"]

                }

        except ClientError:
            pass

        # -----------------------------------------
        # Loop through EC2 Instances
        # -----------------------------------------

        for reservation in reservations:

            for instance in reservation["Instances"]:

                state = instance["State"]["Name"]

                if state == "running":
                    running += 1
                else:
                    stopped += 1

                instance_name = "N/A"

                for tag in instance.get("Tags", []):

                    if tag["Key"] == "Name":
                        instance_name = tag["Value"]
                        break

                instance_id = instance["InstanceId"]

                instance_type = instance["InstanceType"]

                private_ip = instance.get(
                    "PrivateIpAddress",
                    "-"
                )

                system_status = status_lookup.get(
                    instance_id,
                    {}
                ).get(
                    "system_status",
                    "-"
                )

                instance_status = status_lookup.get(
                    instance_id,
                    {}
                ).get(
                    "instance_status",
                    "-"
                )

                instance_list.append({

                    "region": region,

                    "instance_name": instance_name,

                    "instance_id": instance_id,

                    "instance_type": instance_type,

                    "state": state,

                    "private_ip": private_ip,

                    "system_status": system_status,

                    "instance_status": instance_status

                })

    return {

        "running": running,

        "stopped": stopped,

        "total": running + stopped,

        "instances": instance_list

    }