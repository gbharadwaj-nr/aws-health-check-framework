import os


def generate_html_report(

        output_folder,
        account,
        ec2_data,
        rds_data,
        asg_data,
        cloudwatch_data,
        lambda_data
):

    report = ""

    report += f"<h1>AWS Daily Health Check</h1>"

    report += "<div class='summary'>"

    report += f"<h2>{account['client_name']}</h2>"

    report += f"<b>Business Region :</b> {account['business_region']}<br>"

    report += f"<b>AWS Account :</b> {account['account_id']}"

    report += "</div><br>"

    ####################################################
    # Executive Summary
    ####################################################

    report += "<h2>Executive Summary</h2>"

    report += "<table>"

    report += "<tr><th>Service</th><th>Status</th></tr>"

    report += f"<tr><td>EC2</td><td>{ec2_data['running']} Running / {ec2_data['total']} Total</td></tr>"

    report += f"<tr><td>RDS</td><td>{rds_data['available']} Available / {rds_data['total']}</td></tr>"

    report += f"<tr><td>AutoScaling</td><td>{asg_data['healthy']} Healthy / {asg_data['total']}</td></tr>"

    report += f"<tr><td>CloudWatch</td><td>{cloudwatch_data['alarm_count']} Active Alarms</td></tr>"

    report += f"<tr><td>Lambda</td><td>{lambda_data['healthy']} Healthy / {lambda_data['total']}</td></tr>"

    report += "</table>"

    ####################################################
    # EC2
    ####################################################

    report += "<h2>EC2 Instances</h2>"

    report += "<table>"

    report += "<tr>"

    report += "<th>Region</th>"

    report += "<th>Name</th>"

    report += "<th>Instance ID</th>"

    report += "<th>Status</th>"

    report += "</tr>"

    for i in ec2_data["instances"]:

        report += f"""

<tr>

<td>{i['region']}</td>

<td>{i['instance_name']}</td>

<td>{i['instance_id']}</td>

<td>{i['state']}</td>

</tr>

"""

    report += "</table>"

    ####################################################
    # RDS
    ####################################################

    report += "<h2>RDS Databases</h2>"

    report += "<table>"

    report += "<tr><th>Region</th><th>Database</th><th>Status</th></tr>"

    for db in rds_data["databases"]:

        report += f"""

<tr>

<td>{db['region']}</td>

<td>{db['db_identifier']}</td>

<td>{db['status']}</td>

</tr>

"""

    report += "</table>"

    ####################################################
    # ASG
    ####################################################

    report += "<h2>Auto Scaling Groups</h2>"

    report += "<table>"

    report += "<tr><th>Region</th><th>Name</th><th>Status</th></tr>"

    for a in asg_data["groups"]:

        report += f"""

<tr>

<td>{a['region']}</td>

<td>{a['asg_name']}</td>

<td>{a['status']}</td>

</tr>

"""

    report += "</table>"

    ####################################################
    # CloudWatch
    ####################################################

    report += "<h2>CloudWatch Alarms</h2>"

    report += "<table>"

    report += "<tr><th>Region</th><th>Alarm</th><th>State</th></tr>"

    for alarm in cloudwatch_data["alarms"]:

        report += f"""

<tr>

<td>{alarm['region']}</td>

<td>{alarm['alarm_name']}</td>

<td>{alarm['state']}</td>

</tr>

"""

    report += "</table>"

    ####################################################
    # Lambda
    ####################################################

    report += "<h2>Lambda Functions</h2>"

    report += "<table>"

    report += "<tr><th>Region</th><th>Function</th><th>Status</th></tr>"

    for f in lambda_data["functions"]:

        report += f"""

<tr>

<td>{f['region']}</td>

<td>{f['name']}</td>

<td>{f['status']}</td>

</tr>

"""

    report += "</table>"

    ####################################################
    # Write HTML
    ####################################################

    template = open(
        "templates/report_template.html",
        encoding="utf-8"
    ).read()

    html = template.replace("{{CONTENT}}", report)

    report_file = os.path.join(
        output_folder,
        "Executive_Report.html"
    )

    with open(report_file, "w", encoding="utf-8") as f:

        f.write(html)

    print()

    print("=" * 70)

    print("HTML REPORT GENERATED")

    print("=" * 70)

    print(report_file)

    return report_file