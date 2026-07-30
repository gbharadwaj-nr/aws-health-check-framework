"""
===========================================================
AWS Lambda Health Check
===========================================================
"""

from botocore.exceptions import ClientError


def check_lambda(session, regions):

    healthy = 0
    unhealthy = 0

    functions = []

    for region in regions:

        client = session.client("lambda", region_name=region)

        paginator = client.get_paginator("list_functions")

        try:

            for page in paginator.paginate():

                for function in page["Functions"]:

                    name = function["FunctionName"]

                    lower = name.lower()

                    # ------------------------------------------------------
                    # Skip NON-PRODUCTION Lambdas
                    # ------------------------------------------------------

                    if (
                        "preprod" in lower or
                        "mspreprod" in lower or
                        "sandbox" in lower or
                        "dev" in lower or
                        "test" in lower or
                        "qa" in lower or
                        "uat" in lower
                    ):
                        continue

                    # ------------------------------------------------------
                    # Keep ONLY Production Lambdas
                    # ------------------------------------------------------

                    if (
                        "production" not in lower and
                        "-prod-" not in lower and
                        "_prod_" not in lower and
                        lower.endswith("-prod") is False
                    ):
                        continue

                    runtime = function.get("Runtime", "-")
                    memory = function.get("MemorySize", 0)
                    timeout = function.get("Timeout", 0)

                    state = function.get("State", "Unknown")
                    last_update = function.get(
                        "LastUpdateStatus",
                        "Unknown"
                    )

                    # ------------------------------------------------------
                    # CloudWatch Errors (Last 24 Hours)
                    # ------------------------------------------------------

                    errors = 0

                    try:

                        cloudwatch = session.client(
                            "cloudwatch",
                            region_name=region
                        )

                        metrics = cloudwatch.get_metric_statistics(
                            Namespace="AWS/Lambda",
                            MetricName="Errors",
                            Dimensions=[
                                {
                                    "Name": "FunctionName",
                                    "Value": name
                                }
                            ],
                            StartTime=__import__("datetime").datetime.utcnow()
                                      - __import__("datetime").timedelta(days=1),
                            EndTime=__import__("datetime").datetime.utcnow(),
                            Period=86400,
                            Statistics=["Sum"]
                        )

                        datapoints = metrics.get("Datapoints", [])

                        if datapoints:
                            errors = int(datapoints[0]["Sum"])

                    except Exception:
                        pass

                    # ------------------------------------------------------
                    # Health Evaluation
                    # ------------------------------------------------------

                    if (
                        state == "Active"
                        and last_update == "Successful"
                        and errors == 0
                    ):
                        status = "Healthy"
                        healthy += 1

                    else:
                        status = "Unhealthy"
                        unhealthy += 1

                    functions.append({

                        "region": region,

                        "name": name,

                        "runtime": runtime,

                        "memory": memory,

                        "timeout": timeout,

                        "state": state,

                        "last_update": last_update,

                        "errors": errors,

                        "status": status

                    })

        except ClientError as e:

            print(f"Unable to query Lambda in {region}: {e}")

    return {

        "healthy": healthy,

        "unhealthy": unhealthy,

        "total": healthy + unhealthy,

        "functions": functions

    }