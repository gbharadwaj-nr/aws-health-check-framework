"""
===========================================================
CloudWatch Alarm Health Check Module
===========================================================
"""

from botocore.exceptions import ClientError


def check_cloudwatch(session, regions):
    """
    Collect CloudWatch Alarms in ALARM state

    Returns:
    {
        "alarm_count": int,
        "alarms": []
    }
    """

    alarm_list = []

    for region in regions:

        try:

            cloudwatch = session.client(
                "cloudwatch",
                region_name=region
            )

            paginator = cloudwatch.get_paginator(
                "describe_alarms"
            )

            for page in paginator.paginate(
                StateValue="ALARM"
            ):

                for alarm in page["MetricAlarms"]:

                    alarm_list.append({

                        "region": region,

                        "alarm_name": alarm["AlarmName"],

                        "state": alarm["StateValue"],

                        "reason": alarm["StateReason"],

                        "metric": alarm["MetricName"],

                        "namespace": alarm["Namespace"]

                    })

        except ClientError as e:

            print(f"Unable to query CloudWatch in {region}: {e}")

            continue

    return {

        "alarm_count": len(alarm_list),

        "alarms": alarm_list

    }