# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the SES v2 Search and Filter wrapper.

Every AWS call is stubbed using botocore.stub.Stubber so the tests run
offline without credentials. Each test class covers one wrapper method with
a success case and an error case.
"""

import pytest
import boto3
from datetime import datetime, timezone
from botocore.stub import Stubber

from sesv2_search_filter_wrapper import SesV2SearchFilterWrapper


@pytest.fixture
def sesv2_stubber():
    """Create an SES v2 client and its Stubber."""
    client = boto3.client("sesv2", region_name="us-east-1")
    with Stubber(client) as stubber:
        yield client, stubber
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# CreateConfigurationSet
# ---------------------------------------------------------------------------
class TestCreateConfigurationSet:
    def test_success(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_response(
            "create_configuration_set",
            {},
            {"ConfigurationSetName": "test-set"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        response = wrapper.create_configuration_set("test-set")
        assert response is not None

    def test_already_exists(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "create_configuration_set",
            service_error_code="AlreadyExistsException",
            service_message="Configuration set already exists.",
            expected_params={"ConfigurationSetName": "test-set"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        # AlreadyExistsException is caught and logged without re-raise
        wrapper.create_configuration_set("test-set")


# ---------------------------------------------------------------------------
# CreateTenant
# ---------------------------------------------------------------------------
class TestCreateTenant:
    def test_success(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_response(
            "create_tenant",
            {
                "TenantName": "alpha-tenant",
                "TenantId": "tn-abc123",
                "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/alpha-tenant",
                "CreatedTimestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
            },
            {"TenantName": "alpha-tenant"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.create_tenant("alpha-tenant")
        assert result["TenantId"] == "tn-abc123"

    def test_bad_request(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "create_tenant",
            service_error_code="BadRequestException",
            service_message="Invalid tenant name.",
            expected_params={"TenantName": "bad!name"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        with pytest.raises(Exception) as exc_info:
            wrapper.create_tenant("bad!name")
        assert exc_info.value.response["Error"]["Code"] == "BadRequestException"


# ---------------------------------------------------------------------------
# ListConfigurationSets — uses manual NextToken pagination (NOT a paginator)
# ---------------------------------------------------------------------------
class TestListConfigurationSets:
    def test_success_unfiltered(self, sesv2_stubber):
        """List configuration sets without a filter — single page."""
        client, stubber = sesv2_stubber
        stubber.add_response(
            "list_configuration_sets",
            {
                "ConfigurationSets": ["set-a", "set-b"],
            },
            {},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_configuration_sets()
        assert result == ["set-a", "set-b"]

    def test_success_filtered(self, sesv2_stubber):
        """List configuration sets with a filter — single page."""
        client, stubber = sesv2_stubber
        stubber.add_response(
            "list_configuration_sets",
            {
                "ConfigurationSets": ["test-filter-set"],
            },
            {"Filter": {"CONFIGURATION_SET_NAME_CONTAINS": "test"}},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_configuration_sets(
            filter_key="CONFIGURATION_SET_NAME_CONTAINS",
            filter_value="test",
        )
        assert result == ["test-filter-set"]

    def test_bad_request(self, sesv2_stubber):
        """ListConfigurationSets raises BadRequestException."""
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "list_configuration_sets",
            service_error_code="BadRequestException",
            service_message="Invalid filter.",
            expected_params={},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        with pytest.raises(Exception) as exc_info:
            wrapper.list_configuration_sets()
        assert exc_info.value.response["Error"]["Code"] == "BadRequestException"

    def test_pagination(self, sesv2_stubber):
        """List configuration sets with manual NextToken pagination."""
        client, stubber = sesv2_stubber
        # Page 1
        stubber.add_response(
            "list_configuration_sets",
            {
                "ConfigurationSets": ["set-a"],
                "NextToken": "token-page-2",
            },
            {"PageSize": 1},
        )
        # Page 2
        stubber.add_response(
            "list_configuration_sets",
            {
                "ConfigurationSets": ["set-b"],
            },
            {"PageSize": 1, "NextToken": "token-page-2"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_configuration_sets(page_size=1)
        assert result == ["set-a", "set-b"]


# ---------------------------------------------------------------------------
# ListEmailIdentities — uses manual NextToken pagination (NOT a paginator)
# ---------------------------------------------------------------------------
class TestListEmailIdentities:
    def test_success_unfiltered(self, sesv2_stubber):
        """List email identities without a filter — single page."""
        client, stubber = sesv2_stubber
        stubber.add_response(
            "list_email_identities",
            {
                "EmailIdentities": [
                    {
                        "IdentityType": "EMAIL_ADDRESS",
                        "IdentityName": "user@example.com",
                        "SendingEnabled": False,
                        "VerificationStatus": "PENDING",
                    }
                ],
            },
            {},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_email_identities()
        assert len(result) == 1
        assert result[0]["IdentityName"] == "user@example.com"

    def test_success_filtered(self, sesv2_stubber):
        """List email identities with a filter — single page."""
        client, stubber = sesv2_stubber
        stubber.add_response(
            "list_email_identities",
            {
                "EmailIdentities": [
                    {
                        "IdentityType": "DOMAIN",
                        "IdentityName": "example.com",
                        "SendingEnabled": False,
                        "VerificationStatus": "PENDING",
                    }
                ],
            },
            {"Filter": {"IDENTITY_NAME_CONTAINS": "example"}},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_email_identities(
            filter_key="IDENTITY_NAME_CONTAINS", filter_value="example"
        )
        assert len(result) == 1
        assert result[0]["IdentityName"] == "example.com"

    def test_bad_request(self, sesv2_stubber):
        """ListEmailIdentities raises BadRequestException."""
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "list_email_identities",
            service_error_code="BadRequestException",
            service_message="Invalid filter.",
            expected_params={},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        with pytest.raises(Exception) as exc_info:
            wrapper.list_email_identities()
        assert exc_info.value.response["Error"]["Code"] == "BadRequestException"

    def test_pagination(self, sesv2_stubber):
        """List email identities with manual NextToken pagination."""
        client, stubber = sesv2_stubber
        # Page 1
        stubber.add_response(
            "list_email_identities",
            {
                "EmailIdentities": [
                    {
                        "IdentityType": "EMAIL_ADDRESS",
                        "IdentityName": "a@example.com",
                        "SendingEnabled": False,
                        "VerificationStatus": "PENDING",
                    }
                ],
                "NextToken": "token-page-2",
            },
            {"PageSize": 1},
        )
        # Page 2
        stubber.add_response(
            "list_email_identities",
            {
                "EmailIdentities": [
                    {
                        "IdentityType": "DOMAIN",
                        "IdentityName": "example.com",
                        "SendingEnabled": False,
                        "VerificationStatus": "PENDING",
                    }
                ],
            },
            {"PageSize": 1, "NextToken": "token-page-2"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_email_identities(page_size=1)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# ListTenants — uses manual NextToken pagination
# ---------------------------------------------------------------------------
class TestListTenants:
    def test_success_unfiltered(self, sesv2_stubber):
        """List tenants without a filter — single page."""
        client, stubber = sesv2_stubber
        stubber.add_response(
            "list_tenants",
            {
                "Tenants": [
                    {
                        "TenantName": "alpha",
                        "TenantId": "tn-001",
                        "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/alpha",
                        "CreatedTimestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
                    }
                ],
            },
            {},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_tenants()
        assert len(result) == 1
        assert result[0]["TenantName"] == "alpha"

    def test_success_filtered(self, sesv2_stubber):
        """List tenants with a filter — single page."""
        client, stubber = sesv2_stubber
        stubber.add_response(
            "list_tenants",
            {
                "Tenants": [
                    {
                        "TenantName": "customer-alpha",
                        "TenantId": "tn-002",
                        "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/customer-alpha",
                        "CreatedTimestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
                    }
                ],
            },
            {"Filter": {"TENANT_NAME_CONTAINS": "customer"}},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        result = wrapper.list_tenants(
            filter_key="TENANT_NAME_CONTAINS", filter_value="customer"
        )
        assert len(result) == 1
        assert result[0]["TenantName"] == "customer-alpha"

    def test_too_many_requests(self, sesv2_stubber):
        """ListTenants raises TooManyRequestsException."""
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "list_tenants",
            service_error_code="TooManyRequestsException",
            service_message="Rate limit exceeded.",
            expected_params={},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        with pytest.raises(Exception) as exc_info:
            wrapper.list_tenants()
        assert exc_info.value.response["Error"]["Code"] == "TooManyRequestsException"


# ---------------------------------------------------------------------------
# DeleteConfigurationSet
# ---------------------------------------------------------------------------
class TestDeleteConfigurationSet:
    def test_success(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_response(
            "delete_configuration_set",
            {},
            {"ConfigurationSetName": "test-set"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        wrapper.delete_configuration_set("test-set")

    def test_not_found(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "delete_configuration_set",
            service_error_code="NotFoundException",
            service_message="Configuration set not found.",
            expected_params={"ConfigurationSetName": "missing-set"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        # NotFoundException is caught and logged without re-raise
        wrapper.delete_configuration_set("missing-set")


# ---------------------------------------------------------------------------
# DeleteTenant
# ---------------------------------------------------------------------------
class TestDeleteTenant:
    def test_success(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_response(
            "delete_tenant",
            {},
            {"TenantName": "alpha-tenant"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        wrapper.delete_tenant("alpha-tenant")

    def test_not_found(self, sesv2_stubber):
        client, stubber = sesv2_stubber
        stubber.add_client_error(
            "delete_tenant",
            service_error_code="NotFoundException",
            service_message="Tenant not found.",
            expected_params={"TenantName": "missing-tenant"},
        )
        wrapper = SesV2SearchFilterWrapper(client)
        # NotFoundException is caught and logged without re-raise
        wrapper.delete_tenant("missing-tenant")
