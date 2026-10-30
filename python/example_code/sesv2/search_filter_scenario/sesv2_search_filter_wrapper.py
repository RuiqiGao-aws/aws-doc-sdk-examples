# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Amazon SES v2 Search and Filter Wrapper

This module provides a wrapper class for Amazon SES v2 API operations that
demonstrate the new filter support for list operations. The wrapper covers
ListConfigurationSets, ListEmailIdentities, and ListTenants with their new
filter parameters, as well as create and delete operations for setup and cleanup.
"""

import logging
from datetime import datetime, timezone

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.sesv2.SesV2SearchFilterWrapper.decl]
class SesV2SearchFilterWrapper:
    """Encapsulates Amazon SES v2 search and filter operations."""

    def __init__(self, sesv2_client):
        """
        Initializes the SesV2SearchFilterWrapper with an SES v2 client.

        :param sesv2_client: A Boto3 SES v2 client.
        """
        self.sesv2_client = sesv2_client

    # snippet-end:[python.example_code.sesv2.SesV2SearchFilterWrapper.decl]

    # snippet-start:[python.example_code.sesv2.CreateConfigurationSet]
    def create_configuration_set(self, configuration_set_name):
        """
        Creates a configuration set.

        :param configuration_set_name: The name of the configuration set to create.
        :return: The response from the CreateConfigurationSet operation.
        """
        try:
            response = self.sesv2_client.create_configuration_set(
                ConfigurationSetName=configuration_set_name
            )
            logger.info("Created configuration set '%s'.", configuration_set_name)
            return response
        except ClientError as err:
            if err.response["Error"]["Code"] == "AlreadyExistsException":
                logger.warning(
                    "Configuration set '%s' already exists. Skipping creation.",
                    configuration_set_name,
                )
            else:
                logger.error(
                    "Couldn't create configuration set '%s'. Error: %s: %s",
                    configuration_set_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
    # snippet-end:[python.example_code.sesv2.CreateConfigurationSet]

    # snippet-start:[python.example_code.sesv2.CreateTenant]
    def create_tenant(self, tenant_name):
        """
        Creates a tenant.

        :param tenant_name: The name of the tenant to create.
        :return: A dictionary with the tenant's ID and ARN.
        """
        try:
            response = self.sesv2_client.create_tenant(TenantName=tenant_name)
            logger.info(
                "Created tenant '%s' with ID '%s'.",
                tenant_name,
                response.get("TenantId", "N/A"),
            )
            return response
        except ClientError as err:
            if err.response["Error"]["Code"] == "BadRequestException":
                logger.error(
                    "Bad request when creating tenant '%s'. Verify the tenant name "
                    "is valid. Error: %s",
                    tenant_name,
                    err.response["Error"]["Message"],
                )
            else:
                logger.error(
                    "Couldn't create tenant '%s'. Error: %s: %s",
                    tenant_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
            raise
    # snippet-end:[python.example_code.sesv2.CreateTenant]

    # snippet-start:[python.example_code.sesv2.ListConfigurationSets]
    def list_configuration_sets(self, filter_key=None, filter_value=None, page_size=None):
        """
        Lists configuration sets, optionally applying a filter. Uses manual
        NextToken-based pagination since ListConfigurationSets does not support
        the get_paginator() interface.

        :param filter_key: Optional filter key for narrowing results.
        :param filter_value: Optional filter value to match against.
        :param page_size: Optional page size for each request.
        :return: A list of configuration set name strings.
        """
        try:
            all_config_sets = list()
            next_token = None

            while True:
                kwargs = dict()
                if filter_key and filter_value:
                    kwargs["Filter"] = {filter_key: filter_value}
                if page_size is not None:
                    kwargs["PageSize"] = page_size
                if next_token is not None:
                    kwargs["NextToken"] = next_token

                response = self.sesv2_client.list_configuration_sets(**kwargs)
                config_sets = response.get("ConfigurationSets", list())
                all_config_sets.extend(config_sets)

                next_token = response.get("NextToken", None)
                if next_token is None:
                    break

            logger.info(
                "Listed %d configuration set(s)%s.",
                len(all_config_sets),
                f" with filter {filter_key}={filter_value}" if filter_key else "",
            )
            return all_config_sets
        except ClientError as err:
            if err.response["Error"]["Code"] == "BadRequestException":
                logger.error(
                    "Bad request when listing configuration sets. Verify the filter "
                    "key and value are valid. Error: %s",
                    err.response["Error"]["Message"],
                )
            else:
                logger.error(
                    "Couldn't list configuration sets. Error: %s: %s",
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
            raise
    # snippet-end:[python.example_code.sesv2.ListConfigurationSets]

    # snippet-start:[python.example_code.sesv2.ListEmailIdentities]
    def list_email_identities(self, filter_key=None, filter_value=None, page_size=None):
        """
        Lists email identities, optionally applying a filter. Uses manual
        NextToken-based pagination since ListEmailIdentities does not support
        the get_paginator() interface.

        :param filter_key: Optional filter key for narrowing results.
        :param filter_value: Optional filter value to match against.
        :param page_size: Optional page size for each request.
        :return: A list of IdentityInfo dictionaries.
        """
        try:
            all_identities = list()
            next_token = None

            while True:
                kwargs = dict()
                if filter_key and filter_value:
                    kwargs["Filter"] = {filter_key: filter_value}
                if page_size is not None:
                    kwargs["PageSize"] = page_size
                if next_token is not None:
                    kwargs["NextToken"] = next_token

                response = self.sesv2_client.list_email_identities(**kwargs)
                identities = response.get("EmailIdentities", list())
                all_identities.extend(identities)

                next_token = response.get("NextToken", None)
                if next_token is None:
                    break

            logger.info(
                "Listed %d email identit(ies)%s.",
                len(all_identities),
                f" with filter {filter_key}={filter_value}" if filter_key else "",
            )
            return all_identities
        except ClientError as err:
            if err.response["Error"]["Code"] == "BadRequestException":
                logger.error(
                    "Bad request when listing email identities. Verify the filter "
                    "key and value are valid. Error: %s",
                    err.response["Error"]["Message"],
                )
            else:
                logger.error(
                    "Couldn't list email identities. Error: %s: %s",
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
            raise
    # snippet-end:[python.example_code.sesv2.ListEmailIdentities]

    # snippet-start:[python.example_code.sesv2.ListTenants]
    def list_tenants(self, filter_key=None, filter_value=None, page_size=None):
        """
        Lists tenants, optionally applying a filter. Uses manual NextToken-based
        pagination for consistency with the other list operations.

        :param filter_key: Optional filter key for narrowing results.
        :param filter_value: Optional filter value to match against.
        :param page_size: Optional page size for each request.
        :return: A list of TenantInfo dictionaries.
        """
        try:
            all_tenants = list()
            next_token = None

            while True:
                kwargs = dict()
                if filter_key and filter_value:
                    kwargs["Filter"] = {filter_key: filter_value}
                if page_size is not None:
                    kwargs["PageSize"] = page_size
                if next_token is not None:
                    kwargs["NextToken"] = next_token

                response = self.sesv2_client.list_tenants(**kwargs)
                tenants = response.get("Tenants", list())
                all_tenants.extend(tenants)

                next_token = response.get("NextToken", None)
                if next_token is None:
                    break

            logger.info(
                "Listed %d tenant(s)%s.",
                len(all_tenants),
                f" with filter {filter_key}={filter_value}" if filter_key else "",
            )
            return all_tenants
        except ClientError as err:
            if err.response["Error"]["Code"] == "TooManyRequestsException":
                logger.error(
                    "Rate limit exceeded when listing tenants. Implement backoff "
                    "and retry. Error: %s",
                    err.response["Error"]["Message"],
                )
            else:
                logger.error(
                    "Couldn't list tenants. Error: %s: %s",
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
            raise
    # snippet-end:[python.example_code.sesv2.ListTenants]

    # snippet-start:[python.example_code.sesv2.DeleteConfigurationSet]
    def delete_configuration_set(self, configuration_set_name):
        """
        Deletes a configuration set.

        :param configuration_set_name: The name of the configuration set to delete.
        """
        try:
            self.sesv2_client.delete_configuration_set(
                ConfigurationSetName=configuration_set_name
            )
            logger.info("Deleted configuration set '%s'.", configuration_set_name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "NotFoundException":
                logger.warning(
                    "Configuration set '%s' not found. It may already be deleted.",
                    configuration_set_name,
                )
            else:
                logger.error(
                    "Couldn't delete configuration set '%s'. Error: %s: %s",
                    configuration_set_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
    # snippet-end:[python.example_code.sesv2.DeleteConfigurationSet]

    # snippet-start:[python.example_code.sesv2.DeleteTenant]
    def delete_tenant(self, tenant_name):
        """
        Deletes a tenant.

        :param tenant_name: The name of the tenant to delete.
        """
        try:
            self.sesv2_client.delete_tenant(TenantName=tenant_name)
            logger.info("Deleted tenant '%s'.", tenant_name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "NotFoundException":
                logger.warning(
                    "Tenant '%s' not found. It may already be deleted.",
                    tenant_name,
                )
            else:
                logger.error(
                    "Couldn't delete tenant '%s'. Error: %s: %s",
                    tenant_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
    # snippet-end:[python.example_code.sesv2.DeleteTenant]
