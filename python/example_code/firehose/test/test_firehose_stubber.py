# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the Amazon Data Firehose Hello example (firehose_hello.py).

Uses botocore.stub.Stubber exclusively — no real AWS calls, no credentials required.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
import pytest
from botocore.stub import Stubber

from firehose_hello import hello_firehose


@pytest.fixture
def firehose_client():
    """Create a Firehose client for testing."""
    client = boto3.client("firehose", region_name="us-east-1")
    return client


@pytest.fixture
def firehose_stubber(firehose_client):
    """Create a Stubber for the Firehose client."""
    with Stubber(firehose_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


def test_list_delivery_streams_with_streams(firehose_client, firehose_stubber, capsys):
    """Verifies that when streams exist, the function returns their names."""
    firehose_stubber.add_response(
        "list_delivery_streams",
        {
            "DeliveryStreamNames": ["stream-1", "stream-2"],
            "HasMoreDeliveryStreams": False,
        },
    )

    response = hello_firehose(firehose_client)

    assert response["DeliveryStreamNames"] == ["stream-1", "stream-2"]
    assert response["HasMoreDeliveryStreams"] is False

    captured = capsys.readouterr()
    assert "stream-1" in captured.out
    assert "stream-2" in captured.out
    assert "Found 2 Firehose stream(s)" in captured.out


def test_list_delivery_streams_empty(firehose_client, firehose_stubber, capsys):
    """Verifies correct behavior when no streams exist."""
    firehose_stubber.add_response(
        "list_delivery_streams",
        {
            "DeliveryStreamNames": [],
            "HasMoreDeliveryStreams": False,
        },
    )

    response = hello_firehose(firehose_client)

    assert response["DeliveryStreamNames"] == []
    assert response["HasMoreDeliveryStreams"] is False

    captured = capsys.readouterr()
    assert "No Firehose delivery streams found in this region." in captured.out


def test_list_delivery_streams_has_more(firehose_client, firehose_stubber, capsys):
    """Verifies that the HasMoreDeliveryStreams flag is handled when True."""
    firehose_stubber.add_response(
        "list_delivery_streams",
        {
            "DeliveryStreamNames": ["stream-1"],
            "HasMoreDeliveryStreams": True,
        },
    )

    response = hello_firehose(firehose_client)

    assert response["DeliveryStreamNames"] == ["stream-1"]
    assert response["HasMoreDeliveryStreams"] is True

    captured = capsys.readouterr()
    assert "stream-1" in captured.out
    assert "Additional delivery streams exist" in captured.out


def test_list_delivery_streams_service_unavailable(firehose_client, firehose_stubber):
    """Verifies error handling for ServiceUnavailableException."""
    firehose_stubber.add_client_error(
        "list_delivery_streams",
        service_error_code="ServiceUnavailableException",
        service_message="The service is unavailable.",
    )

    with pytest.raises(firehose_client.exceptions.ServiceUnavailableException):
        hello_firehose(firehose_client)
