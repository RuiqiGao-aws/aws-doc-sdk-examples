# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for kms_hello.py using botocore.stub.Stubber.
These tests run offline with no AWS credentials required.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
import pytest
from botocore.exceptions import ClientError
from botocore.stub import Stubber

from kms_hello import hello_kms


class TestHelloKms:
    """Tests for the hello_kms function."""

    def test_generate_random_success(self):
        """Test that hello_kms returns 32 bytes of random data on success."""
        client = boto3.client("kms", region_name="us-east-1")
        stubber = Stubber(client)
        expected_bytes = os.urandom(32)

        stubber.add_response(
            "generate_random",
            {"Plaintext": expected_bytes},
            {"NumberOfBytes": 32},
        )
        stubber.activate()

        result = hello_kms(kms_client=client)

        assert result is not None
        assert len(result) == 32
        assert result == expected_bytes
        stubber.assert_no_pending_responses()

    def test_generate_random_internal_error(self):
        """Test that hello_kms raises ClientError on KMSInternalException."""
        client = boto3.client("kms", region_name="us-east-1")
        stubber = Stubber(client)

        stubber.add_client_error(
            "generate_random",
            service_error_code="KMSInternalException",
            service_message="An internal exception occurred.",
        )
        stubber.activate()

        with pytest.raises(ClientError) as exc_info:
            hello_kms(kms_client=client)

        assert exc_info.value.response["Error"]["Code"] == "KMSInternalException"
        stubber.assert_no_pending_responses()

    def test_generate_random_dependency_timeout(self):
        """Test that hello_kms raises ClientError on DependencyTimeoutException."""
        client = boto3.client("kms", region_name="us-east-1")
        stubber = Stubber(client)

        stubber.add_client_error(
            "generate_random",
            service_error_code="DependencyTimeoutException",
            service_message="The system timed out while trying to fulfill the request.",
        )
        stubber.activate()

        with pytest.raises(ClientError) as exc_info:
            hello_kms(kms_client=client)

        assert (
            exc_info.value.response["Error"]["Code"] == "DependencyTimeoutException"
        )
        stubber.assert_no_pending_responses()
