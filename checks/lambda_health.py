"""
===========================================================
Lambda Health Check
===========================================================
"""

from datetime import datetime, timedelta, timezone


def check_lambda(session, regions):

    lambda_functions = []

    healthy = 0
    unhealthy = 0

    print("\n")
    print("=" * 70)
    print("LAMBDA HEALTH")
    print("=" * 70)

    found_lambda = False

    for region in regions:

        lambda_client = session.client("lambda", region_name=region)
        cloudwatch = session.client("cloudwatch", region_name=region)

        paginator = lambda_client.get_paginator("list_functions")

        for page in paginator.paginate():

            for function in page["Functions"]:

                name = function["FunctionName"]

                # --------------------------------------------------
                # Only Production Lambdas
                # --------------------------------------------------

                lower = name.lower()

                if (
                    "prod" not in lower and
                    "production" not in lower
                ):
                    continue

                found_lambda = True

                runtime = function.get("Runtime", "-")
                memory = function.get("MemorySize", "-")
                timeout = function.get("Timeout", "-")
                state = function.get("State", "Unknown")
                modified = function.get("LastModified", "-")

                # --------------------------------------------------
                # CloudWatch Errors
                # --------------------------------------------------

                end = datetime.now(timezone.utc)
                start = end - timedelta(hours=24)

                response = cloudwatch.get_metric_statistics(
                    Namespace="AWS/Lambda",
                    MetricName="Errors",
                    Dimensions=[
                        {
                            "Name": "FunctionName",
                            "Value": name
                        }
                    ],
                    StartTime=start,
                    EndTime=end,
                    Period=86400,
                    Statistics=["Sum"]
                )

                datapoints = response["Datapoints"]

                errors = 0

                if datapoints:
                    errors = int(datapoints[0]["Sum"])

                if state == "Active" and errors == 0:
                    status = "Healthy"
                    healthy += 1
                else:
                    status = "Unhealthy"
                    unhealthy += 1

                print(f"{name}")
                print(f"  Region       : {region}")
                print(f"  Runtime      : {runtime}")
                print(f"  Memory       : {memory} MB")
                print(f"  Timeout      : {timeout} sec")
                print(f"  State        : {state}")
                print(f"  Errors(24h)  : {errors}")
                print(f"  Status       : {status}")
                print()

                lambda_functions.append({

                    "region": region,
                    "name": name,
                    "runtime": runtime,
                    "memory": memory,
                    "timeout": timeout,
                    "state": state,
                    "last_modified": modified,
                    "errors": errors,
                    "status": status

                })

    if not found_lambda:

        print("No Production Lambda Functions Found.")

    print("=" * 70)
    print("LAMBDA SUMMARY")
    print("=" * 70)

    print(f"Healthy Functions   : {healthy}")
    print(f"Unhealthy Functions : {unhealthy}")
    print(f"Total Functions     : {healthy + unhealthy}")

    return {

        "healthy": healthy,
        "unhealthy": unhealthy,
        "total": healthy + unhealthy,
        "functions": lambda_functions

    }