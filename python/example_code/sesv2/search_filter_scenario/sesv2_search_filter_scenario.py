# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Amazon SES v2 Search and Filter Scenario

This scenario demonstrates the new filter support for list operations in
Amazon SES v2. It walks through creating configuration sets, email identities,
and tenants, then uses the new filter parameters on ListConfigurationSets,
ListEmailIdentities, and ListTenants to narrow results. Finally, it demonstrates
pagination with filters and cleans up created resources.

Steps:
1. Create multiple configuration sets, email identities, and tenants.
2. List all configuration sets (unfiltered) as a baseline.
3. Filter configuration sets using the new ConfigurationSetFilter.
4. List all email identities (unfiltered) as a baseline.
5. Filter email identities using the new IdentityFilter.
6. List all tenants (unfiltered) as a baseline.
7. Filter tenants using the new ListTenantsFilter.
8. Demonstrate pagination with filters.
9. Clean up all created resources.
"""

# snippet-start:[python.example_code.sesv2.SearchFilterBasics]
import logging
import boto3
from botocore.exceptions import ClientError
from sesv2_search_filter_wrapper import SesV2SearchFilterWrapper

logger = logging.getLogger(__name__)

# Resource names used during the scenario.
CONFIG_SET_NAMES = [
    "marketing-campaign-set",
    "transactional-email-set",
    "test-filter-set",
]
EMAIL_IDENTITIES = [
    "marketing@example.com",
    "support@example.com",
    "example.com",
]
TENANT_NAMES = [
    "customer-alpha",
    "customer-beta",
    "internal-testing",
]


def run_scenario(wrapper):
    """
    Runs the SES v2 Search and Filter scenario end-to-end.

    :param wrapper: A SesV2SearchFilterWrapper instance.
    """
    created_config_sets = list()
    created_identities = list()
    created_tenants = list()

    try:
        # --- Setup: create resources ---
        print("\n--- Setup: Creating configuration sets ---")
        for name in CONFIG_SET_NAMES:
            try:
                wrapper.create_configuration_set(name)
                created_config_sets.append(name)
                print(f"  Created configuration set: {name}")
            except ClientError:
                print(f"  Skipped configuration set (may already exist): {name}")

        print("\n--- Setup: Creating email identities ---")
        for identity in EMAIL_IDENTITIES:
            try:
                wrapper.sesv2_client.create_email_identity(EmailIdentity=identity)
                created_identities.append(identity)
                print(f"  Created email identity: {identity}")
            except ClientError as err:
                if err.response["Error"]["Code"] == "TooManyRequestsException":
                    logger.warning("Rate limited creating identity '%s'.", identity)
                else:
                    print(f"  Skipped email identity: {identity}")

        print("\n--- Setup: Creating tenants ---")
        for name in TENANT_NAMES:
            try:
                wrapper.create_tenant(name)
                created_tenants.append(name)
                print(f"  Created tenant: {name}")
            except ClientError:
                print(f"  Skipped tenant (may already exist): {name}")

        # --- Step 1: List all configuration sets (unfiltered) ---
        print("\n--- Step 1: List all configuration sets (unfiltered) ---")
        all_config_sets = wrapper.list_configuration_sets()
        print(f"  Found {len(all_config_sets)} configuration set(s).")
        for cs in all_config_sets:
            print(f"    - {cs}")

        # --- Step 2: Filter configuration sets ---
        print("\n--- Step 2: Filter configuration sets (name contains 'test') ---")
        filtered_config_sets = wrapper.list_configuration_sets(
            filter_key="CONFIGURATION_SET_NAME_CONTAINS", filter_value="test"
        )
        print(f"  Found {len(filtered_config_sets)} matching configuration set(s).")
        for cs in filtered_config_sets:
            print(f"    - {cs}")

        # --- Step 3: List all email identities (unfiltered) ---
        print("\n--- Step 3: List all email identities (unfiltered) ---")
        all_identities = wrapper.list_email_identities()
        print(f"  Found {len(all_identities)} email identit(ies).")
        for ident in all_identities:
            print(
                f"    - {ident.get('IdentityName', 'N/A')} "
                f"({ident.get('IdentityType', 'N/A')})"
            )

        # --- Step 4: Filter email identities ---
        print("\n--- Step 4: Filter email identities (by type or name) ---")
        filtered_identities = wrapper.list_email_identities(
            filter_key="IDENTITY_NAME_CONTAINS", filter_value="example"
        )
        print(f"  Found {len(filtered_identities)} matching identit(ies).")
        for ident in filtered_identities:
            print(
                f"    - {ident.get('IdentityName', 'N/A')} "
                f"({ident.get('IdentityType', 'N/A')})"
            )

        # --- Step 5: List all tenants (unfiltered) ---
        print("\n--- Step 5: List all tenants (unfiltered) ---")
        all_tenants = wrapper.list_tenants()
        print(f"  Found {len(all_tenants)} tenant(s).")
        for t in all_tenants:
            print(f"    - {t.get('TenantName', 'N/A')} (ID: {t.get('TenantId', 'N/A')})")

        # --- Step 6: Filter tenants ---
        print("\n--- Step 6: Filter tenants (name contains 'customer') ---")
        filtered_tenants = wrapper.list_tenants(
            filter_key="TENANT_NAME_CONTAINS", filter_value="customer"
        )
        print(f"  Found {len(filtered_tenants)} matching tenant(s).")
        for t in filtered_tenants:
            print(f"    - {t.get('TenantName', 'N/A')} (ID: {t.get('TenantId', 'N/A')})")

        # --- Step 7: Demonstrate pagination with filters ---
        print("\n--- Step 7: Pagination with filter (page_size=1) ---")
        paginated_results = wrapper.list_configuration_sets(
            filter_key="CONFIGURATION_SET_NAME_CONTAINS",
            filter_value="set",
            page_size=1,
        )
        print(f"  Retrieved {len(paginated_results)} configuration set(s) across pages.")
        for cs in paginated_results:
            print(f"    - {cs}")

    finally:
        # --- Cleanup ---
        print("\n--- Cleanup ---")
        for name in created_config_sets:
            try:
                wrapper.delete_configuration_set(name)
                print(f"  Deleted configuration set: {name}")
            except ClientError:
                print(f"  Could not delete configuration set: {name}")

        for identity in created_identities:
            try:
                wrapper.sesv2_client.delete_email_identity(EmailIdentity=identity)
                print(f"  Deleted email identity: {identity}")
            except ClientError:
                print(f"  Could not delete email identity: {identity}")

        for name in created_tenants:
            try:
                wrapper.delete_tenant(name)
                print(f"  Deleted tenant: {name}")
            except ClientError:
                print(f"  Could not delete tenant: {name}")

    print("\n--- Scenario complete ---")


def main():
    """Entry point for the SES v2 Search and Filter scenario."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sesv2_client = boto3.client("sesv2")
    wrapper = SesV2SearchFilterWrapper(sesv2_client)
    run_scenario(wrapper)


if __name__ == "__main__":
    main()
# snippet-end:[python.example_code.sesv2.SearchFilterBasics]
