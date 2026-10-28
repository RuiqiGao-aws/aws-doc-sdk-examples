# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Amazon SES v2 Search and Filter Wrapper

This module provides a wrapper class for Amazon SES v2 operations
that demonstrates the new filter support for list operations on
configuration sets, email identities, and tenants.
"""

import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.sesv2.SesV2SearchFilterWrapper.decl]
class SesV2SearchFilterWrapper:
    """Encapsulates Amazon SES v2 search and filter operations."""

    def __init__(self, sesv2_client):
        """
        Initializes the SesV2SearchFilterWrapper with an SES v2 client.

        :param sesv2_client: A Boto3 Amazon SES v2 client.
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
        except ClientError as error:
            if error.response["Error"]["Code"] == "AlreadyExistsException":
                logger.info(
                    "Configuration set '%s' already exists, skipping creation.",
                    configuration_set_name,
                )
            else:
                logger.exception(
                    "Couldn't create configuration set '%s'.", configuration_set_name
                )
                raise
    # snippet-end:[python.example_code.sesv2.CreateConfigurationSet]

    def create_email_identity(self, email_identity):
        """
        Creates an email identity.

        :param email_identity: The email address or domain to verify.
        :return: The response from the CreateEmailIdentity operation.
        """
        try:
            response = self.sesv2_client.create_email_identity(
                EmailIdentity=email_identity
            )
            logger.info("Created email identity '%s'.", email_identity)
            return response
        except ClientError as error:
            if error.response["Error"]["Code"] == "TooManyRequestsException":
                logger.error(
                    "Too many requests when creating email identity '%s'. "
                    "Retry after a delay.",
                    email_identity,
                )
                raise
            else:
                logger.exception(
                    "Couldn't create email identity '%s'.", email_identity
                )
                raise

    # snippet-start:[python.example_code.sesv2.CreateTenant]
    def create_tenant(self, tenant_name):
        """
        Creates a tenant.

        :param tenant_name: The name of the tenant to create.
        :return: The response from the CreateTenant operation, including
                 TenantName, TenantId, and TenantArn.
        """
        try:
            response = self.sesv2_client.create_tenant(TenantName=tenant_name)
            logger.info("Created tenant '%s'.", tenant_name)
            return response
        except ClientError as error:
            if error.response["Error"]["Code"] == "BadRequestException":
                logger.error(
                    "Bad request when creating tenant '%s': %s",
                    tenant_name,
                    error.response["Error"]["Message"],
                )
            else:
                logger.exception("Couldn't create tenant '%s'.", tenant_name)
            raise
    # snippet-end:[python.example_code.sesv2.CreateTenant]

    # snippet-start:[python.example_code.sesv2.ListConfigurationSets]
    def list_configuration_sets(self, filter_key=None, filter_value=None, page_size=None):
        """
        Lists configuration sets, optionally applying a filter.

        Uses the paginator to automatically handle pagination.

        :param filter_key: Optional filter key (e.g., 'CONFIGURATION_SET_NAME_CONTAINS').
        :param filter_value: Optional filter value to match against.
        :param page_size: Optional number of results per page.
        :return: A list of configuration set name strings.
        """
        try:
            configuration_sets = list()
            params = dict()
            if filter_key and filter_value:
                params["Filter"] = {filter_key: filter_value}
            if page_size is not None:
                params["PageSize"] = page_size

            paginator = self.sesv2_client.get_paginator("list_configuration_sets")
            for page in paginator.paginate(**params):
                configuration_sets.extend(page.get("ConfigurationSets", list()))

            logger.info(
                "Listed %d configuration sets.", len(configuration_sets)
            )
            return configuration_sets
        except ClientError as error:
            if error.response["Error"]["Code"] == "BadRequestException":
                logger.error(
                    "Bad request listing configuration sets: %s",
                    error.response["Error"]["Message"],
                )
            else:
                logger.exception("Couldn't list configuration sets.")
            raise
    # snippet-end:[python.example_code.sesv2.ListConfigurationSets]

    # snippet-start:[python.example_code.sesv2.ListEmailIdentities]
    def list_email_identities(self, filter_key=None, filter_value=None, page_size=None):
        """
        Lists email identities, optionally applying a filter.

        Uses the paginator to automatically handle pagination.

        :param filter_key: Optional filter key (e.g., 'IDENTITY_NAME_CONTAINS',
                           'IDENTITY_TYPE', 'VERIFICATION_STATUS').
        :param filter_value: Optional filter value to match against.
        :param page_size: Optional number of results per page.
        :return: A list of IdentityInfo dictionaries.
        """
        try:
            identities = list()
            params = dict()
            if filter_key and filter_value:
                params["Filter"] = {filter_key: filter_value}
            if page_size is not None:
                params["PageSize"] = page_size

            paginator = self.sesv2_client.get_paginator("list_email_identities")
            for page in paginator.paginate(**params):
                identities.extend(page.get("EmailIdentities", list()))

            logger.info("Listed %d email identities.", len(identities))
            return identities
        except ClientError as error:
            if error.response["Error"]["Code"] == "BadRequestException":
                logger.error(
                    "Bad request listing email identities: %s",
                    error.response["Error"]["Message"],
                )
            else:
                logger.exception("Couldn't list email identities.")
            raise
    # snippet-end:[python.example_code.sesv2.ListEmailIdentities]

    # snippet-start:[python.example_code.sesv2.ListTenants]
    def list_tenants(self, filter_key=None, filter_value=None, page_size=None):
        """
        Lists tenants, optionally applying a filter.

        Uses the paginator to automatically handle pagination.

        :param filter_key: Optional filter key (e.g., 'TENANT_NAME_CONTAINS',
                           'SENDING_STATUS').
        :param filter_value: Optional filter value to match against.
        :param page_size: Optional number of results per page.
        :return: A list of TenantInfo dictionaries.
        """
        try:
            tenants = list()
            params = dict()
            if filter_key and filter_value:
                params["Filter"] = {filter_key: filter_value}
            if page_size is not None:
                params["PageSize"] = page_size

            paginator = self.sesv2_client.get_paginator("list_tenants")
            for page in paginator.paginate(**params):
                tenants.extend(page.get("Tenants", list()))

            logger.info("Listed %d tenants.", len(tenants))
            return tenants
        except ClientError as error:
            if error.response["Error"]["Code"] == "TooManyRequestsException":
                logger.error(
                    "Too many requests listing tenants. Retry with backoff."
                )
            else:
                logger.exception("Couldn't list tenants.")
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
        except ClientError as error:
            if error.response["Error"]["Code"] == "NotFoundException":
                logger.info(
                    "Configuration set '%s' not found, skipping deletion.",
                    configuration_set_name,
                )
            else:
                logger.exception(
                    "Couldn't delete configuration set '%s'.",
                    configuration_set_name,
                )
                raise
    # snippet-end:[python.example_code.sesv2.DeleteConfigurationSet]

    def delete_email_identity(self, email_identity):
        """
        Deletes an email identity.

        :param email_identity: The email address or domain to delete.
        """
        try:
            self.sesv2_client.delete_email_identity(EmailIdentity=email_identity)
            logger.info("Deleted email identity '%s'.", email_identity)
        except ClientError as error:
            if error.response["Error"]["Code"] == "NotFoundException":
                logger.info(
                    "Email identity '%s' not found, skipping deletion.",
                    email_identity,
                )
            else:
                logger.exception(
                    "Couldn't delete email identity '%s'.", email_identity
                )
                raise

    # snippet-start:[python.example_code.sesv2.DeleteTenant]
    def delete_tenant(self, tenant_name):
        """
        Deletes a tenant.

        :param tenant_name: The name of the tenant to delete.
        """
        try:
            self.sesv2_client.delete_tenant(TenantName=tenant_name)
            logger.info("Deleted tenant '%s'.", tenant_name)
        except ClientError as error:
            if error.response["Error"]["Code"] == "NotFoundException":
                logger.info(
                    "Tenant '%s' not found, skipping deletion.", tenant_name
                )
            else:
                logger.exception("Couldn't delete tenant '%s'.", tenant_name)
                raise
    # snippet-end:[python.example_code.sesv2.DeleteTenant]
