"""
===========================================================
Microsoft Teams Notification
===========================================================
"""

import os
import json
import urllib.request


def send_teams_notification(
    account,
    ec2_data,
    rds_data,
    asg_data,
    cloudwatch_data,
    lambda_data,
    batch_log_data=None
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

    if batch_log_data and batch_log_data.get("status") in ("FLAG_FOUND", "ERROR"):
        status = "Attention Required"

    facts = [
        {"name": "Business Region", "value": account["business_region"]},
        {"name": "AWS Account", "value": account["account_id"]},
        {"name": "Overall Status", "value": status},
        {"name": "EC2", "value": f"{ec2_data['running']} Running / {ec2_data['total']} Total"},
        {"name": "RDS", "value": f"{rds_data['available']} Available / {rds_data['total']} Total"},
        {"name": "Auto Scaling", "value": f"{asg_data['healthy']} Healthy / {asg_data['total']} Total"},
        {"name": "CloudWatch", "value": f"{cloudwatch_data['alarm_count']} Active Alarm(s)"},
        {"name": "Lambda", "value": f"{lambda_data['healthy']} Healthy / {lambda_data['total']} Total"},
    ]

    # ---------------------------------------------------------
    # Batch Log Facts
    # ---------------------------------------------------------

    if batch_log_data:

        facts.append({
            "name": "Batch Log Status",
            "value": batch_log_data.get("status", "N/A")
        })

        facts.append({
            "name": "Batch Log Group",
            "value": batch_log_data.get("log_group") or "Not Found"
        })

        facts.append({
            "name": "Batch Log Stream",
            "value": batch_log_data.get("log_stream") or "Not Found"
        })

        facts.append({
            "name": f"Keyword '{batch_log_data.get('keyword', 'flag')}' Matches (24h)",
            "value": str(batch_log_data.get("match_count", 0))
        })

        if batch_log_data.get("error"):
            facts.append({
                "name": "Batch Log Error",
                "value": batch_log_data["error"]
            })

    message = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "AWS Daily Health Check",
        "title": f"AWS Daily Health Check - {account['client_name']}",
        "sections": [
            {
                "activityTitle": f"Environment : {account['client_name']}",
                "facts": facts
            }
        ]
    }

    # ---------------------------------------------------------
    # Batch Log Matched Entries (separate section)
    # ---------------------------------------------------------

    if batch_log_data and batch_log_data.get("matches"):

        sample_matches = batch_log_data["matches"][:10]

        match_lines = "\n\n".join(
            f"**{m['timestamp']}**: {m['message']}"
            for m in sample_matches
        )

        remaining = batch_log_data["match_count"] - len(sample_matches)
        if remaining > 0:
            match_lines += f"\n\n_...and {remaining} more entr(ies)_"

        message["sections"].append({
            "activityTitle": "Batch Log Matched Entries",
            "text": match_lines
        })

    # ---------------------------------------------------------
    # Send
    # ---------------------------------------------------------

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