# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Test configuration for the SES v2 Search and Filter scenario tests.

Adds the parent directory to sys.path so that the wrapper and scenario modules
can be imported without requiring a package install.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
