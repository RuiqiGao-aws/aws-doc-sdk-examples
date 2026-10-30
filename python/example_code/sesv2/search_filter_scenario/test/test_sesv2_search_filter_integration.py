# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Integration test for the SES v2 Search and Filter scenario.

This test runs the full scenario against real AWS and is only executed
after merge (marked with @pytest.mark.integ). It is deselected by the
offline CI step which runs: pytest -m "not integ"
"""

import pytest
import boto3
from unittest.mock import patch

from sesv2_search_filter_wrapper import SesV2SearchFilterWrapper
from sesv2_search_filter_scenario import run_scenario


@pytest.mark.integ
def test_run_search_filter_scenario():
    """Run the SES v2 search and filter scenario end-to-end against real AWS."""
    sesv2_client = boto3.client("sesv2", region_name="us-east-1")
    wrapper = SesV2SearchFilterWrapper(sesv2_client)

    try:
        run_scenario(wrapper)
    except Exception as exc:
        pytest.fail(f"Scenario failed with exception: {exc}")
