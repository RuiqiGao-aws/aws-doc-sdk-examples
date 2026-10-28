# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for sesv2_search_filter_wrapper.py

Uses botocore.stub.Stubber to stub every AWS call. Each wrapper method
has a success case and an error case that asserts the specific exception.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import boto3
from botocore.stub import Stubber
from sesv2_search_filter_wrapper import SesV2SearchFilterWrapper


@pytest.fixture
def sesv2_stubber():
    """Create an SES v2 client with a Stubber attached."""
    client = boto3.client("sesv2", region_name="us-east-1")
    stubber = Stubber(client)
    wrapper = SesV2SearchFilterWrapper(client)
    stubber.activate()
    yield wrapper, stubber
    stubber.deactivate()


# ---------------------------------------------------------------------------
# CreateConfigurationSet
# ---------------------------------------------------------------------------
class TestCreateConfigurationSet:
    def test_create_configuration_set_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "create_configuration_set",
            {},
            {"ConfigurationSetName": "test-set"},
        )
        response = wrapper.create_configuration_set("test-set")
        assert response is not None
        stubber.assert_no_pending_responses()

    def test_create_configuration_set_already_exists(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "create_configuration_set",
            service_error_code="AlreadyExistsException",
            service_message="Configuration set already exists.",
            expected_params={"ConfigurationSetName": "test-set"},
        )
        # AlreadyExistsException is handled gracefully (does not raise)
        wrapper.create_configuration_set("test-set")
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# CreateEmailIdentity
# ---------------------------------------------------------------------------
class TestCreateEmailIdentity:
    def test_create_email_identity_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "create_email_identity",
            {
                "IdentityType": "EMAIL_ADDRESS",
                "VerifiedForSendingStatus": False,
                "DkimAttributes": {
                    "SigningEnabled": False,
                    "Status": "NOT_STARTED",
                    "Tokens": [],
                },
            },
            {"EmailIdentity": "test@example.com"},
        )
        response = wrapper.create_email_identity("test@example.com")
        assert response["IdentityType"] == "EMAIL_ADDRESS"
        stubber.assert_no_pending_responses()

    def test_create_email_identity_too_many_requests(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "create_email_identity",
            service_error_code="TooManyRequestsException",
            service_message="Rate exceeded.",
            expected_params={"EmailIdentity": "test@example.com"},
        )
        with pytest.raises(Exception) as exc_info:
            wrapper.create_email_identity("test@example.com")
        assert "TooManyRequestsException" in str(exc_info.value) or "Rate exceeded" in str(exc_info.value)
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# CreateTenant
# ---------------------------------------------------------------------------
class TestCreateTenant:
    def test_create_tenant_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "create_tenant",
            {"TenantName": "my-tenant", "TenantId": "tid-123", "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/my-tenant"},
            {"TenantName": "my-tenant"},
        )
        response = wrapper.create_tenant("my-tenant")
        assert response["TenantName"] == "my-tenant"
        stubber.assert_no_pending_responses()

    def test_create_tenant_bad_request(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "create_tenant",
            service_error_code="BadRequestException",
            service_message="Invalid tenant name.",
            expected_params={"TenantName": "bad!name"},
        )
        with pytest.raises(Exception) as exc_info:
            wrapper.create_tenant("bad!name")
        assert "BadRequestException" in str(exc_info.value) or "Invalid" in str(exc_info.value)
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# ListConfigurationSets
# ---------------------------------------------------------------------------
class TestListConfigurationSets:
    def test_list_configuration_sets_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "list_configuration_sets",
            {
                "ConfigurationSets": ["set-a", "set-b"],
            },
            {},
        )
        result = wrapper.list_configuration_sets()
        assert result == ["set-a", "set-b"]
        stubber.assert_no_pending_responses()

    def test_list_configuration_sets_with_filter(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "list_configuration_sets",
            {
                "ConfigurationSets": ["test-filter-set"],
            },
            {"Filter": {"CONFIGURATION_SET_NAME_CONTAINS": "test"}},
        )
        result = wrapper.list_configuration_sets(
            filter_key="CONFIGURATION_SET_NAME_CONTAINS",
            filter_value="test",
        )
        assert result == ["test-filter-set"]
        stubber.assert_no_pending_responses()

    def test_list_configuration_sets_bad_request(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "list_configuration_sets",
            service_error_code="BadRequestException",
            service_message="Invalid filter.",
            expected_params={"Filter": {"INVALID_KEY": "val"}},
        )
        with pytest.raises(Exception) as exc_info:
            wrapper.list_configuration_sets(
                filter_key="INVALID_KEY", filter_value="val"
            )
        assert "BadRequestException" in str(exc_info.value) or "Invalid" in str(exc_info.value)
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# ListEmailIdentities
# ---------------------------------------------------------------------------
class TestListEmailIdentities:
    def test_list_email_identities_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
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
        result = wrapper.list_email_identities()
        assert len(result) == 1
        assert result[0]["IdentityName"] == "user@example.com"
        stubber.assert_no_pending_responses()

    def test_list_email_identities_with_filter(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
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
        result = wrapper.list_email_identities(
            filter_key="IDENTITY_NAME_CONTAINS",
            filter_value="example",
        )
        assert len(result) == 1
        assert result[0]["IdentityType"] == "DOMAIN"
        stubber.assert_no_pending_responses()

    def test_list_email_identities_bad_request(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "list_email_identities",
            service_error_code="BadRequestException",
            service_message="Invalid filter key.",
            expected_params={"Filter": {"BAD_KEY": "val"}},
        )
        with pytest.raises(Exception) as exc_info:
            wrapper.list_email_identities(filter_key="BAD_KEY", filter_value="val")
        assert "BadRequestException" in str(exc_info.value) or "Invalid" in str(exc_info.value)
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# ListTenants
# ---------------------------------------------------------------------------
class TestListTenants:
    def test_list_tenants_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "list_tenants",
            {
                "Tenants": [
                    {
                        "TenantName": "customer-alpha",
                        "TenantId": "tid-001",
                        "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/customer-alpha",
                    }
                ],
            },
            {},
        )
        result = wrapper.list_tenants()
        assert len(result) == 1
        assert result[0]["TenantName"] == "customer-alpha"
        stubber.assert_no_pending_responses()

    def test_list_tenants_with_filter(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "list_tenants",
            {
                "Tenants": [
                    {
                        "TenantName": "customer-alpha",
                        "TenantId": "tid-001",
                        "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/customer-alpha",
                    },
                    {
                        "TenantName": "customer-beta",
                        "TenantId": "tid-002",
                        "TenantArn": "arn:aws:ses:us-east-1:123456789012:tenant/customer-beta",
                    },
                ],
            },
            {"Filter": {"TENANT_NAME_CONTAINS": "customer"}},
        )
        result = wrapper.list_tenants(
            filter_key="TENANT_NAME_CONTAINS", filter_value="customer"
        )
        assert len(result) == 2
        stubber.assert_no_pending_responses()

    def test_list_tenants_too_many_requests(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "list_tenants",
            service_error_code="TooManyRequestsException",
            service_message="Rate exceeded.",
            expected_params={},
        )
        with pytest.raises(Exception) as exc_info:
            wrapper.list_tenants()
        assert "TooManyRequestsException" in str(exc_info.value) or "Rate exceeded" in str(exc_info.value)
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# DeleteConfigurationSet
# ---------------------------------------------------------------------------
class TestDeleteConfigurationSet:
    def test_delete_configuration_set_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "delete_configuration_set",
            {},
            {"ConfigurationSetName": "test-set"},
        )
        wrapper.delete_configuration_set("test-set")
        stubber.assert_no_pending_responses()

    def test_delete_configuration_set_not_found(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "delete_configuration_set",
            service_error_code="NotFoundException",
            service_message="Not found.",
            expected_params={"ConfigurationSetName": "missing-set"},
        )
        # NotFoundException is handled gracefully (does not raise)
        wrapper.delete_configuration_set("missing-set")
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# DeleteEmailIdentity
# ---------------------------------------------------------------------------
class TestDeleteEmailIdentity:
    def test_delete_email_identity_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "delete_email_identity",
            {},
            {"EmailIdentity": "test@example.com"},
        )
        wrapper.delete_email_identity("test@example.com")
        stubber.assert_no_pending_responses()

    def test_delete_email_identity_not_found(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "delete_email_identity",
            service_error_code="NotFoundException",
            service_message="Not found.",
            expected_params={"EmailIdentity": "gone@example.com"},
        )
        # NotFoundException is handled gracefully (does not raise)
        wrapper.delete_email_identity("gone@example.com")
        stubber.assert_no_pending_responses()


# ---------------------------------------------------------------------------
# DeleteTenant
# ---------------------------------------------------------------------------
class TestDeleteTenant:
    def test_delete_tenant_success(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_response(
            "delete_tenant",
            {},
            {"TenantName": "my-tenant"},
        )
        wrapper.delete_tenant("my-tenant")
        stubber.assert_no_pending_responses()

    def test_delete_tenant_not_found(self, sesv2_stubber):
        wrapper, stubber = sesv2_stubber
        stubber.add_client_error(
            "delete_tenant",
            service_error_code="NotFoundException",
            service_message="Not found.",
            expected_params={"TenantName": "gone-tenant"},
        )
        # NotFoundException is handled gracefully (does not raise)
        wrapper.delete_tenant("gone-tenant")
        stubber.assert_no_pending_responses()
