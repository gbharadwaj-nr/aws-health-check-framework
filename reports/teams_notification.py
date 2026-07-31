import os
import json
import urllib.request


def send_teams_notification(
    account,
    ec2_data,
    rds_data,
    asg_data,
    cloudwatch_data,
    lambda_data
):
    """
    Sends AWS Health Check summary to Microsoft Teams.
    """

    webhook = os.getenv("TEAMS_WEBHOOK")

    if not webhook:
        print("Teams webhook not configured.")
        return

    status = "Healthy"

    if (
        cloudwatch_data["alarm_count"] > 0
        or asg_data["unhealthy"] > 0
        or lambda_data["unhealthy"] > 0
    ):
        status = "Attention Required"

    message = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "AWS Daily Health Check",
        "title": f"AWS Daily Health Check - {account['client_name']}",
        "sections": [
            {
                "activityTitle": f"Environment : {account['client_name']}",
                "facts": [
                    {
                        "name": "Business Region",
                        "value": account["business_region"]
                    },
                    {
                        "name": "AWS Account",
                        "value": account["account_id"]
                    },
                    {
                        "name": "Overall Status",
                        "value": status
                    },
                    {
                        "name": "EC2",
                        "value": f"{ec2_data['running']} Running / {ec2_data['total']} Total"
                    },
                    {
                        "name": "RDS",
                        "value": f"{rds_data['available']} Available / {rds_data['total']} Total"
                    },
                    {
                        "name": "Auto Scaling",
                        "value": f"{asg_data['healthy']} Healthy / {asg_data['total']} Total"
                    },
                    {
                        "name": "CloudWatch",
                        "value": f"{cloudwatch_data['alarm_count']} Active Alarm(s)"
                    },
                    {
                        "name": "Lambda",
                        "value": f"{lambda_data['healthy']} Healthy / {lambda_data['total']} Total"
                    }
                ]
            }
        ]
    }

    try:

        request = urllib.request.Request(
            webhook,
            data=json.dumps(message).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        urllib.request.urlopen(request)

        print()
        print("=" * 70)
        print("Teams Notification Sent Successfully")
        print("=" * 70)

    except Exception as e:

        print()
        print("=" * 70)
        print("Failed to send Teams notification")
        print(e)
        print("=" * 70)