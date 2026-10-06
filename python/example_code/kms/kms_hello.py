# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose
    Shows how to get started with AWS Key Management Service (AWS KMS)
    by generating a cryptographically secure random byte string using
    the GenerateRandom API action.
"""

import logging

import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.kms.Hello]
def hello_kms(kms_client=None):
    """
    Use the AWS SDK for Python (Boto3) to create an AWS KMS client and
    generate a 32-byte cryptographically secure random byte string.
    This demonstrates that the KMS service is reachable and the client
    is properly configured.

    :param kms_client: A Boto3 KMS client. If None, a new client is created.
    :return: The random bytes returned by KMS.
    """
    if kms_client is None:
        kms_client = boto3.client("kms")

    try:
        response = kms_client.generate_random(NumberOfBytes=32)
        random_bytes = response["Plaintext"]
        print("Successfully connected to AWS KMS!")
        print(f"Generated {len(random_bytes)} bytes of random data:")
        print(random_bytes.hex())
        return random_bytes
    except ClientError as error:
        error_code = error.response["Error"]["Code"]
        if error_code == "KMSInternalException":
            logger.error("KMS service error: %s", error.response["Error"]["Message"])
            logger.info("The request can be retried.")
        elif error_code == "DependencyTimeoutException":
            logger.error("KMS timed out: %s", error.response["Error"]["Message"])
            logger.info("The request can be retried.")
        else:
            logger.error("KMS error: %s", error.response["Error"]["Message"])
        raise


# snippet-end:[python.example_code.kms.Hello]


if __name__ == "__main__":
    hello_kms()
