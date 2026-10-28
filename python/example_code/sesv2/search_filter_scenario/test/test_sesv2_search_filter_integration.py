# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Integration test for the SES v2 Search and Filter scenario.

This test runs the complete scenario against real AWS services.
It is marked with @pytest.mark.integ and runs only after merge,
not before the PR.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import boto3
from unittest.mock import patch
from sesv2_search_filter_wrapper import SesV2SearchFilterWrapper
from sesv2_search_filter_scenario import run_scenario


@pytest.mark.integ
def test_search_filter_scenario_integration():
    """
    Runs the full Search and Filter scenario against real AWS.

    User input is mocked so the test runs non-interactively.
    Cleanup happens in the finally block of run_scenario itself.
    """
    sesv2_client = boto3.client("sesv2")
    wrapper = SesV2SearchFilterWrapper(sesv2_client)

    # Mock all user input to auto-proceed through prompts
    input_responses = iter(["", "", "", "", "", "", "", "y"])

    def mock_input(prompt=""):
        return next(input_responses, "y")

    try:
        run_scenario(wrapper, input_func=mock_input)
    except Exception as e:
        # If the scenario fails, log but still let cleanup run
        # (it's inside run_scenario's finally block)
        pytest.fail(f"Scenario failed with error: {e}")
