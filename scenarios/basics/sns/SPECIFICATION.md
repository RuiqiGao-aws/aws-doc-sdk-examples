# Amazon SNS Hello World Specification

This document contains the specification for a *Hello Amazon SNS* example. This is a minimal, standalone program that demonstrates how to set up an Amazon SNS client and make a single read-only API call to verify that the client is configured correctly. It is NOT a multi-step scenario, does not create or delete resources, and does not include a wrapper/service class.

### Resources

No additional AWS resources are required. The program simply lists existing SNS topics in the caller's account and region. If no topics exist, the program reports that no topics were found.

### Relevant documentation

* [What is Amazon SNS?](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
* [Amazon SNS API Reference](https://docs.aws.amazon.com/sns/latest/api/Welcome.html)
* [ListTopics API Reference](https://docs.aws.amazon.com/sns/latest/api/API_ListTopics.html)

### API Actions Used

* [ListTopics](https://docs.aws.amazon.com/sns/latest/api/API_ListTopics.html) — Returns a list of the requester's topics. Each call returns up to 100 topics. If there are more topics, a `NextToken` is returned for pagination.

## Hello SNS

This Hello example is a separate, standalone runnable program. It demonstrates the simplest possible interaction with Amazon SNS.

**Operation used:** `ListTopics`

### Program logic

1. Create an Amazon SNS client with default configuration (region, credentials).
2. Call `ListTopics` (no parameters required for the first page).
3. If topics are returned, print each topic's ARN.
4. If no topics are found, print a message indicating no topics exist in the current account/region.
5. Handle errors gracefully and print a meaningful error message.

### Expected output

When topics exist:
```
Hello Amazon SNS! Let's list your topics:

  Topic ARN: arn:aws:sns:us-east-1:123456789012:my-first-topic
  Topic ARN: arn:aws:sns:us-east-1:123456789012:my-second-topic

Found 2 topic(s).
```

When no topics exist:
```
Hello Amazon SNS! Let's list your topics:

No topics found in the current account/region.
```

### Parameters

**ListTopics request:**

| Parameter   | Type   | Required | Description                                                                                  |
|-------------|--------|----------|----------------------------------------------------------------------------------------------|
| `NextToken` | String | No       | Token returned by a previous `ListTopics` call. Omitted on the first call.                   |

**ListTopics response:**

| Field       | Type              | Description                                                                                     |
|-------------|-------------------|-------------------------------------------------------------------------------------------------|
| `Topics`    | Array of Topic    | A list of topic objects. Each object contains a `TopicArn` string field.                        |
| `NextToken` | String            | Token to pass to the next `ListTopics` call if there are additional topics. Absent if no more.  |

### Pagination note

`ListTopics` returns up to 100 topics per call. For this Hello example, retrieving the first page is sufficient to demonstrate connectivity. Implementations MAY optionally paginate through all results using `NextToken`, but this is not required.

## Test Requirements (Python)

The test file MUST be named `test_sns_stubber.py` and use `botocore.stub.Stubber` exclusively. These are unit tests ONLY — NO integration tests, NO real AWS calls, NO AWS credentials required.

### Test file structure

- **File name:** `test_sns_stubber.py`
- **Dependencies:** `pytest`, `boto3`, `botocore` (all in `requirements.txt`)
- **No external helpers:** Do not import `demo_tools`, `demo_helpers`, or any non-pip module.
- **No interactive prompts:** No `input()` calls.

### Required test cases

1. **`test_list_topics_success`** — Stub `ListTopics` to return a response containing two topics. Call the hello function/wrapper. Assert the returned topics list contains the expected ARNs.

2. **`test_list_topics_empty`** — Stub `ListTopics` to return a response with an empty `Topics` list. Call the hello function/wrapper. Assert the result indicates no topics were found (empty list).

3. **`test_list_topics_authorization_error`** — Stub `ListTopics` with `add_client_error` using service error code `AuthorizationError`. Call the hello function/wrapper. Assert that `AuthorizationErrorException` (or the specific `ClientError` with code `AuthorizationError`) is raised.

4. **`test_list_topics_internal_error`** — Stub `ListTopics` with `add_client_error` using service error code `InternalError`. Call the hello function/wrapper. Assert that `InternalErrorException` (or the specific `ClientError` with code `InternalError`) is raised.

### Test pattern

```
For each test:
  1. Create a boto3 SNS client
  2. Create a Stubber for the client
  3. Add the appropriate stubbed response or error via add_response / add_client_error
  4. Activate the Stubber
  5. Call the hello/list_topics function, passing the stubbed client
  6. Assert the expected result or exception
  7. Verify the Stubber has no remaining expected responses (stubber.assert_no_pending_responses)
```

### Constraints

- Every AWS API call in every test MUST be intercepted by a Stubber — no real AWS calls.
- Tests MUST pass with `pytest test_sns_stubber.py -v` without AWS credentials (runs in Docker offline).
- NO integration tests, no `@pytest.mark.integ`, no classes or functions named `*Integration*` or `*_integ`.
- NO creation, use, or deletion of real AWS resources in any test.
- For error tests, assert the SPECIFIC error code (e.g., `AuthorizationError`, `InternalError`), not generic `ClientError`.

### requirements.txt

```
pytest
boto3
botocore
```

## Errors

| Action       | Exception                    | Handling                                                                                   |
|--------------|------------------------------|--------------------------------------------------------------------------------------------|
| `ListTopics` | `AuthorizationErrorException` | Notify the user that they do not have permission to list SNS topics. Suggest checking IAM policies. |

## Metadata

| action / scenario   | metadata file       | metadata key      |
|---------------------|---------------------|-------------------|
| `ListTopics`        | sns_metadata.yaml   | sns_ListTopics    |
| `SNS Hello`         | sns_metadata.yaml   | sns_Hello         |
