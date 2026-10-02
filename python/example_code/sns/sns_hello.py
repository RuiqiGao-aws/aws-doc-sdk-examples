# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to get started with Amazon Simple Notification Service (Amazon SNS)
by listing the SNS topics in your account.
"""

import logging
from typing import Any, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.sns.Hello]
def hello_sns(sns_client: Any) -> List[str]:
    """
    Use the AWS SDK for Python (Boto3) to create an Amazon SNS client and list
    the topics in your account. This example uses the default settings specified
    in your shared credentials and config files.

    :param sns_client: A Boto3 Amazon SNS client object.
    :return: A list of topic ARNs found in the account.
    """
    print("Hello, Amazon SNS! Let's list your topics:\n")

    try:
        response = sns_client.list_topics()
        topics = response.get("Topics", list())
        topic_arns = [topic["TopicArn"] for topic in topics]

        if topic_arns:
            for arn in topic_arns:
                print(f"  Topic ARN: {arn}")
            print(f"\nFound {len(topic_arns)} topic(s).")
        else:
            print("No topics found in the current account/region.")

        return topic_arns

    except ClientError as error:
        if error.response["Error"]["Code"] == "AuthorizationError":
            logger.error(
                "You don't have permission to list SNS topics. "
                "Check your IAM policies."
            )
        logger.error("Couldn't list SNS topics. Here's why: %s", error)
        raise


# snippet-end:[python.example_code.sns.Hello]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sns_client = boto3.client("sns")
    hello_sns(sns_client)
