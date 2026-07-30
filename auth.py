"""
===========================================================
Authentication Module
===========================================================
"""

import boto3
from config import ROLE_NAME


def assume_role(account):

    sts = boto3.client("sts")

    role_arn = f"arn:aws:iam::{account['account_id']}:role/{ROLE_NAME}"

    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="HealthCheckSession"
    )

    credentials = response["Credentials"]

    session = boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"]
    )

    return session