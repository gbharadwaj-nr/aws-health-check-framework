"""
===========================================================
Batch Log Health Check
Uses boto3 CloudWatch Logs APIs ONLY.
===========================================================
"""

from datetime import datetime, timedelta, timezone


def _get_client(session, region):
    return session.client("logs", region_name=region)


def _matches_app_pattern(name):
    name = name.lower()
    return "production-application" in name or "prod-application" in name


def _find_latest_log_group(logs_client):
    paginator = logs_client.get_paginator("describe_log_groups")

    matching = []

    for page in paginator.paginate():
        for group in page.get("logGroups", []):
            if _matches_app_pattern(group.get("logGroupName", "")):
                matching.append(group)

    if not matching:
        return None

    matching.sort(key=lambda g: g.get("creationTime", 0), reverse=True)

    return matching[0]["logGroupName"]


def _find_latest_runbatch_stream(logs_client, log_group_name):
    paginator = logs_client.get_paginator("describe_log_streams")

    matching = []

    try:
        for page in paginator.paginate(
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
        ):
            for stream in page.get("logStreams", []):
                if "runbatch.log" in stream.get("logStreamName", "").lower():
                    matching.append(stream)

            if matching:
                break

    except logs_client.exceptions.ResourceNotFoundException:
        return None

    if not matching:
        return None

    return matching[0]["logStreamName"]


def _search_stream_for_keyword(logs_client, log_group_name, log_stream_name,
                               keyword, hours=24):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)

    start_ms = int(start_time.timestamp() * 1000)
    end_ms = int(end_time.timestamp() * 1000)

    matches = []
    next_token = None

    while True:
        params = {
            "logGroupName": log_group_name,
            "logStreamNames": [log_stream_name],
            "startTime": start_ms,
            "endTime": end_ms,
            "filterPattern": f'"{keyword}"',
        }

        if next_token:
            params["nextToken"] = next_token

        response = logs_client.filter_log_events(**params)

        for event in response.get("events", []):
            matches.append({
                "timestamp": datetime.fromtimestamp(
                    event["timestamp"] / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "message": event.get("message", "").strip(),
            })

        next_token = response.get("nextToken")

        if not next_token:
            break

    return matches


def check_batch_log(session, regions, keyword="flag", hours=24):
    result = {
        "log_group": None,
        "log_stream": None,
        "region": None,
        "keyword": keyword,
        "matches": [],
        "match_count": 0,
        "status": "NOT_FOUND",
        "error": None,
    }

    for region in regions:
        try:
            logs_client = _get_client(session, region)

            log_group_name = _find_latest_log_group(logs_client)
            if not log_group_name:
                continue

            log_stream_name = _find_latest_runbatch_stream(
                logs_client, log_group_name
            )
            if not log_stream_name:
                result.update({
                    "log_group": log_group_name,
                    "region": region,
                    "status": "NOT_FOUND",
                })
                continue

            matches = _search_stream_for_keyword(
                logs_client, log_group_name, log_stream_name, keyword, hours
            )

            result.update({
                "log_group": log_group_name,
                "log_stream": log_stream_name,
                "region": region,
                "matches": matches,
                "match_count": len(matches),
                "status": "FLAG_FOUND" if matches else "OK",
            })

            return result

        except Exception as exc:
            result["error"] = str(exc)
            result["status"] = "ERROR"
            continue

    return result