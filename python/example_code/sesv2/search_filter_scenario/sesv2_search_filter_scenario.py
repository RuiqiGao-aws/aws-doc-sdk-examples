# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Amazon SES v2 Search and Filter Scenario

This scenario demonstrates the new filter support for list operations in
Amazon Simple Email Service (SES) API v2. It walks through creating
configuration sets, email identities, and tenants, then uses the new filter
parameters on ListConfigurationSets, ListEmailIdentities, and ListTenants
to narrow results. Finally, it demonstrates that pagination works correctly
in conjunction with the filter parameter.

Steps:
1. Setup: Create configuration sets, email identities, and tenants.
2. List all configuration sets (unfiltered baseline).
3. Filter configuration sets using ConfigurationSetFilter.
4. List all email identities (unfiltered baseline).
5. Filter email identities using IdentityFilter.
6. List all tenants (unfiltered baseline).
7. Filter tenants using ListTenantsFilter.
8. Demonstrate pagination with filters.
9. Cleanup: Delete all resources created during setup.
"""

# snippet-start:[python.example_code.sesv2.SearchFilterBasics]
import logging
import boto3
from botocore.exceptions import ClientError
from sesv2_search_filter_wrapper import SesV2SearchFilterWrapper

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Resource names created by the scenario (used for setup and cleanup).
# ---------------------------------------------------------------------------
CONFIGURATION_SET_NAMES = [
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


def _ask(prompt, default="y"):
    """Prompt the user for input with a default."""
    response = input(f"{prompt} [{default}]: ").strip()
    return response if response else default


def run_scenario(wrapper, input_func=None):
    """
    Runs the Search and Filter SES Resources scenario.

    :param wrapper: A SesV2SearchFilterWrapper instance.
    :param input_func: Optional callable to override built-in input().
    """
    global_input = input_func if input_func else input

    print("=" * 72)
    print("Welcome to the Amazon SES v2 Search and Filter Scenario")
    print("=" * 72)
    print(
        "\nThis scenario demonstrates the new filter capability on list\n"
        "operations for configuration sets, email identities, and tenants.\n"
    )

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    print("-" * 72)
    print("SETUP: Creating SES resources...")
    print("-" * 72)

    created_config_sets = list()
    created_identities = list()
    created_tenants = list()

    # Create configuration sets
    for name in CONFIGURATION_SET_NAMES:
        try:
            wrapper.create_configuration_set(name)
            created_config_sets.append(name)
            print(f"  ✓ Configuration set created: {name}")
        except ClientError:
            print(f"  ✗ Could not create configuration set: {name}")

    # Create email identities
    for identity in EMAIL_IDENTITIES:
        try:
            wrapper.create_email_identity(identity)
            created_identities.append(identity)
            print(f"  ✓ Email identity created: {identity}")
        except ClientError:
            print(f"  ✗ Could not create email identity: {identity}")

    # Create tenants
    for tenant_name in TENANT_NAMES:
        try:
            wrapper.create_tenant(tenant_name)
            created_tenants.append(tenant_name)
            print(f"  ✓ Tenant created: {tenant_name}")
        except ClientError:
            print(f"  ✗ Could not create tenant: {tenant_name}")

    try:
        # ------------------------------------------------------------------
        # Step 1: List all configuration sets (unfiltered)
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 1: List all configuration sets (unfiltered)")
        print("-" * 72)
        all_config_sets = wrapper.list_configuration_sets()
        print(f"  Found {len(all_config_sets)} configuration set(s):")
        for cs in all_config_sets:
            print(f"    - {cs}")

        global_input("\nPress Enter to continue...")

        # ------------------------------------------------------------------
        # Step 2: Filter configuration sets
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 2: Filter configuration sets by name substring")
        print("-" * 72)
        filter_substring = "test"
        print(
            f"  Applying filter: CONFIGURATION_SET_NAME_CONTAINS = '{filter_substring}'"
        )
        filtered_config_sets = wrapper.list_configuration_sets(
            filter_key="CONFIGURATION_SET_NAME_CONTAINS",
            filter_value=filter_substring,
        )
        print(f"  Found {len(filtered_config_sets)} matching configuration set(s):")
        for cs in filtered_config_sets:
            print(f"    - {cs}")

        global_input("\nPress Enter to continue...")

        # ------------------------------------------------------------------
        # Step 3: List all email identities (unfiltered)
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 3: List all email identities (unfiltered)")
        print("-" * 72)
        all_identities = wrapper.list_email_identities()
        print(f"  Found {len(all_identities)} identity(ies):")
        for ident in all_identities:
            print(
                f"    - {ident.get('IdentityName', 'N/A')} "
                f"(Type: {ident.get('IdentityType', 'N/A')}, "
                f"Status: {ident.get('VerificationStatus', 'N/A')})"
            )

        global_input("\nPress Enter to continue...")

        # ------------------------------------------------------------------
        # Step 4: Filter email identities
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 4: Filter email identities by name substring")
        print("-" * 72)
        identity_filter = "example"
        print(f"  Applying filter: IDENTITY_NAME_CONTAINS = '{identity_filter}'")
        filtered_identities = wrapper.list_email_identities(
            filter_key="IDENTITY_NAME_CONTAINS",
            filter_value=identity_filter,
        )
        print(f"  Found {len(filtered_identities)} matching identity(ies):")
        for ident in filtered_identities:
            print(
                f"    - {ident.get('IdentityName', 'N/A')} "
                f"(Type: {ident.get('IdentityType', 'N/A')}, "
                f"Status: {ident.get('VerificationStatus', 'N/A')})"
            )

        global_input("\nPress Enter to continue...")

        # ------------------------------------------------------------------
        # Step 5: List all tenants (unfiltered)
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 5: List all tenants (unfiltered)")
        print("-" * 72)
        all_tenants = wrapper.list_tenants()
        print(f"  Found {len(all_tenants)} tenant(s):")
        for t in all_tenants:
            print(
                f"    - {t.get('TenantName', 'N/A')} "
                f"(ID: {t.get('TenantId', 'N/A')})"
            )

        global_input("\nPress Enter to continue...")

        # ------------------------------------------------------------------
        # Step 6: Filter tenants
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 6: Filter tenants by name substring")
        print("-" * 72)
        tenant_filter = "customer"
        print(f"  Applying filter: TENANT_NAME_CONTAINS = '{tenant_filter}'")
        filtered_tenants = wrapper.list_tenants(
            filter_key="TENANT_NAME_CONTAINS",
            filter_value=tenant_filter,
        )
        print(f"  Found {len(filtered_tenants)} matching tenant(s):")
        for t in filtered_tenants:
            print(
                f"    - {t.get('TenantName', 'N/A')} "
                f"(ID: {t.get('TenantId', 'N/A')})"
            )

        global_input("\nPress Enter to continue...")

        # ------------------------------------------------------------------
        # Step 7: Demonstrate pagination with filters
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("STEP 7: Demonstrate pagination with filters")
        print("-" * 72)
        print(
            "  Listing configuration sets with filter and PageSize=1 to show "
            "paginated retrieval..."
        )
        paginated_results = wrapper.list_configuration_sets(
            filter_key="CONFIGURATION_SET_NAME_CONTAINS",
            filter_value="set",
            page_size=1,
        )
        print(
            f"  Retrieved {len(paginated_results)} configuration set(s) across "
            "multiple pages:"
        )
        for cs in paginated_results:
            print(f"    - {cs}")

        global_input("\nPress Enter to continue to cleanup...")

    finally:
        # ------------------------------------------------------------------
        # Cleanup
        # ------------------------------------------------------------------
        print("\n" + "-" * 72)
        print("CLEANUP: Deleting resources created by this scenario")
        print("-" * 72)

        cleanup_choice = global_input(
            "Do you want to clean up all resources? (y/n) [y]: "
        )
        if cleanup_choice.lower() in ("y", "yes", ""):
            for name in created_config_sets:
                try:
                    wrapper.delete_configuration_set(name)
                    print(f"  ✓ Deleted configuration set: {name}")
                except ClientError:
                    print(f"  ✗ Could not delete configuration set: {name}")

            for identity in created_identities:
                try:
                    wrapper.delete_email_identity(identity)
                    print(f"  ✓ Deleted email identity: {identity}")
                except ClientError:
                    print(f"  ✗ Could not delete email identity: {identity}")

            for tenant_name in created_tenants:
                try:
                    wrapper.delete_tenant(tenant_name)
                    print(f"  ✓ Deleted tenant: {tenant_name}")
                except ClientError:
                    print(f"  ✗ Could not delete tenant: {tenant_name}")
        else:
            print("  Skipping cleanup. Resources remain in your account.")

    print("\n" + "=" * 72)
    print("Scenario complete! You demonstrated:")
    print("  - Listing resources without filters (full result sets)")
    print("  - Using the new filter capability on list operations")
    print("  - Pagination working correctly with filters")
    print("=" * 72)


def main():
    """Entry point for the scenario."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sesv2_client = boto3.client("sesv2")
    wrapper = SesV2SearchFilterWrapper(sesv2_client)
    run_scenario(wrapper)


if __name__ == "__main__":
    main()
# snippet-end:[python.example_code.sesv2.SearchFilterBasics]
