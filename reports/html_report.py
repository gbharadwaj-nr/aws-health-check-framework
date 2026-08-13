"""
===========================================================
HTML Report Generator
===========================================================
"""

import os
import shutil


def generate_html_report(
    output_folder,
    account,
    ec2_data,
    rds_data,
    asg_data,
    cloudwatch_data,
    lambda_data,
    batch_log_data=None
):
    """
    Generates the Executive HTML Report.
    """

    report = ""

    # ==========================================================
    # Header
    # ==========================================================

    report += "<h1>AWS Daily Health Check Report</h1>"

    report += "<div class='summary'>"

    report += f"<h2>{account['client_name']}</h2>"
    report += f"<b>Business Region :</b> {account['business_region']}<br>"
    report += f"<b>AWS Account :</b> {account['account_id']}"

    report += "</div><br>"

    # ==========================================================
    # Executive Summary
    # ==========================================================

    report += "<h2>Executive Summary</h2>"

    report += """
    <table>
        <tr>
            <th>Service</th>
            <th>Status</th>
        </tr>
    """

    report += f"<tr><td>EC2</td><td>{ec2_data['running']} Running / {ec2_data['total']} Total</td></tr>"
    report += f"<tr><td>RDS</td><td>{rds_data['available']} Available / {rds_data['total']} Total</td></tr>"
    report += f"<tr><td>Auto Scaling</td><td>{asg_data['healthy']} Healthy / {asg_data['total']} Total</td></tr>"
    report += f"<tr><td>CloudWatch</td><td>{cloudwatch_data['alarm_count']} Active Alarm(s)</td></tr>"
    report += f"<tr><td>Lambda</td><td>{lambda_data['healthy']} Healthy / {lambda_data['total']} Total</td></tr>"
    report += f"<tr><td>Batch Log</td><td>{batch_log_data['status']} ({batch_log_data['match_count']} match(es) in 24h)</td></tr>"

    report += "</table><br>"

    # ==========================================================
    # EC2
    # ==========================================================

    report += "<h2>EC2 Instances</h2>"

    report += """
    <table>
    <tr>
        <th>Region</th>
        <th>Name</th>
        <th>Instance ID</th>
        <th>Status</th>
    </tr>
    """

    for instance in ec2_data["instances"]:

        report += f"""
        <tr>
            <td>{instance['region']}</td>
            <td>{instance['instance_name']}</td>
            <td>{instance['instance_id']}</td>
            <td>{instance['state']}</td>
        </tr>
        """

    report += "</table><br>"

    # ==========================================================
    # RDS
    # ==========================================================

    report += "<h2>RDS Databases</h2>"

    report += """
    <table>
    <tr>
        <th>Region</th>
        <th>Database</th>
        <th>Status</th>
    </tr>
    """

    for db in rds_data["databases"]:

        report += f"""
        <tr>
            <td>{db['region']}</td>
            <td>{db['db_identifier']}</td>
            <td>{db['status']}</td>
        </tr>
        """

    report += "</table><br>"

    # ==========================================================
    # ASG
    # ==========================================================

    report += "<h2>Auto Scaling Groups</h2>"

    report += """
    <table>
    <tr>
        <th>Region</th>
        <th>ASG Name</th>
        <th>Status</th>
    </tr>
    """

    for group in asg_data["groups"]:

        report += f"""
        <tr>
            <td>{group['region']}</td>
            <td>{group['asg_name']}</td>
            <td>{group['status']}</td>
        </tr>
        """

    report += "</table><br>"

    # ==========================================================
    # CloudWatch
    # ==========================================================

    report += "<h2>CloudWatch Alarms</h2>"

    report += """
    <table>
    <tr>
        <th>Region</th>
        <th>Alarm Name</th>
        <th>State</th>
    </tr>
    """

    for alarm in cloudwatch_data["alarms"]:

        report += f"""
        <tr>
            <td>{alarm['region']}</td>
            <td>{alarm['alarm_name']}</td>
            <td>{alarm['state']}</td>
        </tr>
        """

    report += "</table><br>"

    # ==========================================================
    # Lambda
    # ==========================================================

    report += "<h2>Lambda Functions</h2>"

    report += """
    <table>
    <tr>
        <th>Region</th>
        <th>Function Name</th>
        <th>Status</th>
    </tr>
    """

    for function in lambda_data["functions"]:

        report += f"""
        <tr>
            <td>{function['region']}</td>
            <td>{function['name']}</td>
            <td>{function['status']}</td>
        </tr>
        """

    report += "</table><br>"

    # ==========================================================
    # Batch Log Check
    # ==========================================================

    if batch_log_data:

        report += "<h2>Batch Log Check</h2>"

        report += """
        <table>
        <tr>
            <th>Attribute</th>
            <th>Value</th>
        </tr>
        """

        report += f"<tr><td>Region</td><td>{batch_log_data.get('region') or 'N/A'}</td></tr>"
        report += f"<tr><td>Log Group</td><td>{batch_log_data.get('log_group') or 'Not Found'}</td></tr>"
        report += f"<tr><td>Log Stream</td><td>{batch_log_data.get('log_stream') or 'Not Found'}</td></tr>"
        report += f"<tr><td>Keyword</td><td>{batch_log_data.get('keyword', 'flag')}</td></tr>"
        report += f"<tr><td>Status</td><td>{batch_log_data.get('status')}</td></tr>"
        report += f"<tr><td>Matches (24h)</td><td>{batch_log_data.get('match_count', 0)}</td></tr>"

        if batch_log_data.get("error"):
            report += f"<tr><td>Error</td><td>{batch_log_data['error']}</td></tr>"

        report += "</table><br>"

        if batch_log_data.get("matches"):

            report += "<h3>Matched Log Entries</h3>"

            report += """
            <table>
            <tr>
                <th>Timestamp</th>
                <th>Message</th>
            </tr>
            """

            for entry in batch_log_data["matches"]:

                message = (
                    entry["message"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                report += f"""
                <tr>
                    <td>{entry['timestamp']}</td>
                    <td>{message}</td>
                </tr>
                """

            report += "</table>"

    # ==========================================================
    # Read HTML Template
    # ==========================================================

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    template_path = os.path.join(
        BASE_DIR,
        "templates",
        "report_template.html"
    )

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    html = template.replace("{{CONTENT}}", report)

    # ==========================================================
    # Save Client Report
    # ==========================================================

    report_file = os.path.join(
        output_folder,
        "Executive_Report.html"
    )

    with open(report_file, "w", encoding="utf-8") as file:
        file.write(html)

    # ==========================================================
    # Save Latest Report
    # ==========================================================

    latest_folder = os.path.join(
        BASE_DIR,
        "output",
        "latest"
    )

    os.makedirs(latest_folder, exist_ok=True)

    shutil.copy(
        report_file,
        os.path.join(
            latest_folder,
            "Executive_Report.html"
        )
    )

    # ==========================================================
    # Console Output
    # ==========================================================

    print()
    print("=" * 70)
    print("HTML REPORT GENERATED")
    print("=" * 70)
    print(report_file)
    print()

    print("Latest Report")
    print(os.path.join(
        latest_folder,
        "Executive_Report.html"
    ))

    return report_file