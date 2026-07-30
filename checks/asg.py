"""
===========================================================
Auto Scaling Group Health Check Module to collect ASG Inventory and Health Status
===========================================================
"""

from botocore.exceptions import ClientError


def check_asg(session, regions):

    healthy = 0
    unhealthy = 0

    asg_list = []

    for region in regions:

        try:

            client = session.client(
                "autoscaling",
                region_name=region
            )

            response = client.describe_auto_scaling_groups()

        except ClientError as e:

            print(f"Unable to query ASG in {region}: {e}")
            continue

        groups = response["AutoScalingGroups"]

        if len(groups) == 0:
            continue

        for group in groups:

            healthy_instances = 0
            unhealthy_instances = 0

            for instance in group["Instances"]:

                if instance["HealthStatus"] == "Healthy":
                    healthy_instances += 1
                else:
                    unhealthy_instances += 1

            status = "Healthy"

            if unhealthy_instances > 0:
                status = "Unhealthy"
                unhealthy += 1
            else:
                healthy += 1

            asg_list.append({

                "region": region,
                "asg_name": group["AutoScalingGroupName"],
                "desired": group["DesiredCapacity"],
                "current": len(group["Instances"]),
                "healthy": healthy_instances,
                "unhealthy": unhealthy_instances,
                "status": status

            })

    return {

        "healthy": healthy,
        "unhealthy": unhealthy,
        "total": len(asg_list),
        "groups": asg_list

    }