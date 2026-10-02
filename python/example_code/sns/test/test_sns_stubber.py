# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for sns_hello.py using botocore Stubber.

These tests run offline — no AWS credentials or real AWS calls required.
Run with: pytest test_sns_stubber.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import boto3
from botocore.stub import Stubber
from botocore.exceptions import ClientError

from sns_hello import hello_sns


@pytest.fixture
def sns_client():
    """Create a boto3 SNS client for stubbing."""
    return boto3.client("sns", region_name="us-east-1")


def test_list_topics_success(sns_client):
    """Stub ListTopics to return two topics and verify the returned ARNs."""
    stubber = Stubber(sns_client)

    response = {
        "Topics": [
            {"TopicArn": "arn:aws:sns:us-east-1:123456789012:my-first-topic"},
            {"TopicArn": "arn:aws:sns:us-east-1:123456789012:my-second-topic"},
        ]
    }

    stubber.add_response("list_topics", response, {})
    stubber.activate()

    topic_arns = hello_sns(sns_client)

    assert len(topic_arns) == 2
    assert "arn:aws:sns:us-east-1:123456789012:my-first-topic" in topic_arns
    assert "arn:aws:sns:us-east-1:123456789012:my-second-topic" in topic_arns

    stubber.assert_no_pending_responses()


def test_list_topics_empty(sns_client):
    """Stub ListTopics to return an empty Topics list and verify empty result."""
    stubber = Stubber(sns_client)

    response = {"Topics": list()}

    stubber.add_response("list_topics", response, {})
    stubber.activate()

    topic_arns = hello_sns(sns_client)

    assert len(topic_arns) == 0

    stubber.assert_no_pending_responses()


def test_list_topics_authorization_error(sns_client):
    """Stub ListTopics with AuthorizationError and verify the error is raised."""
    stubber = Stubber(sns_client)

    stubber.add_client_error(
        "list_topics",
        service_error_code="AuthorizationError",
        service_message="User is not authorized to perform sns:ListTopics",
    )
    stubber.activate()

    with pytest.raises(ClientError) as exc_info:
        hello_sns(sns_client)

    assert exc_info.value.response["Error"]["Code"] == "AuthorizationError"

    stubber.assert_no_pending_responses()


def test_list_topics_internal_error(sns_client):
    """Stub ListTopics with InternalError and verify the error is raised."""
    stubber = Stubber(sns_client)

    stubber.add_client_error(
        "list_topics",
        service_error_code="InternalError",
        service_message="An internal service error occurred",
    )
    stubber.activate()

    with pytest.raises(ClientError) as exc_info:
        hello_sns(sns_client)

    assert exc_info.value.response["Error"]["Code"] == "InternalError"

    stubber.assert_no_pending_responses()
