# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to get started with Amazon Data Firehose by listing your delivery
streams using the AWS SDK for Python (Boto3).
"""

import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.firehose.Hello]
def hello_firehose(firehose_client):
    """
    Use the AWS SDK for Python (Boto3) to create an Amazon Data Firehose
    client and list the delivery streams in your account.
    This example uses the default settings specified in your shared credentials
    and config files.

    :param firehose_client: A Boto3 Amazon Data Firehose client object.
    :return: The response from ListDeliveryStreams.
    """
    print("Hello, Amazon Data Firehose! Let's list your delivery streams:\n")

    try:
        response = firehose_client.list_delivery_streams()
        stream_names = response.get("DeliveryStreamNames", list())
        has_more = response.get("HasMoreDeliveryStreams", False)

        if stream_names:
            for name in stream_names:
                print(f"  - {name}")
            print(f"\nFound {len(stream_names)} Firehose stream(s) in this region.")
        else:
            print("No Firehose delivery streams found in this region.")

        if has_more:
            print(
                "\nNote: Additional delivery streams exist beyond those listed. "
                "Use the ExclusiveStartDeliveryStreamName parameter to page "
                "through all streams."
            )

        return response

    except ClientError as error:
        if error.response["Error"]["Code"] == "ServiceUnavailableException":
            logger.error(
                "The Amazon Data Firehose service is temporarily unavailable. "
                "Please retry after a brief delay."
            )
        else:
            logger.error(
                "Couldn't list Firehose delivery streams. Here's why: %s: %s",
                error.response["Error"]["Code"],
                error.response["Error"]["Message"],
            )
        raise


# snippet-end:[python.example_code.firehose.Hello]

if __name__ == "__main__":
    hello_firehose(boto3.client("firehose"))
