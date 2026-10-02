# Amazon Data Firehose Hello World Specification

This document contains a draft specification for a **Hello World** example for *Amazon Data Firehose*. The Hello World example is a minimal, standalone program that verifies the Firehose client is configured correctly by calling the `ListDeliveryStreams` API and printing the results. There is no multi-step scenario, no wrapper class, and no prerequisite resource setup or cleanup.

### Resources

No additional AWS resources are required. The `ListDeliveryStreams` API is a read-only operation that lists existing Firehose streams in the caller's account. The account may have zero or more streams — both cases are handled gracefully.

### Relevant documentation

* [What is Amazon Data Firehose?](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
* [Amazon Data Firehose API Reference](https://docs.aws.amazon.com/firehose/latest/APIReference/Welcome.html)
* [ListDeliveryStreams API Reference](https://docs.aws.amazon.com/firehose/latest/APIReference/API_ListDeliveryStreams.html)

### API Actions Used

* [ListDeliveryStreams](https://docs.aws.amazon.com/firehose/latest/APIReference/API_ListDeliveryStreams.html) — Lists Firehose streams in alphabetical order.

## Hello Amazon Data Firehose

The Hello example uses the **ListDeliveryStreams** API action.

This program performs the following steps:

1. Create an Amazon Data Firehose client with default configuration.
2. Call `ListDeliveryStreams` with no parameters (all defaults) to retrieve up to 10 Firehose stream names.
3. Print the list of Firehose stream names to the console.
   - If streams exist, print each stream name on its own line.
   - If no streams exist, print a friendly message indicating no Firehose streams were found in the current region.
4. If `HasMoreDeliveryStreams` is `true` in the response, print a note indicating that additional streams exist beyond those listed.

### ListDeliveryStreams API Details

**Description:** Lists Firehose streams in alphabetical order by name. Supports pagination via `ExclusiveStartDeliveryStreamName` and a configurable `Limit`.

**Request Parameters (all optional):**

| Parameter | Type | Description |
|-|-|-|
| `DeliveryStreamType` | String | Filter by stream type: `DirectPut`, `KinesisStreamAsSource`, `MSKAsSource`, or `DatabaseAsSource`. If omitted, all types are returned. |
| `ExclusiveStartDeliveryStreamName` | String | Start listing after this stream name (for pagination). Min length 1, max length 64. Pattern: `[a-zA-Z0-9_.-]+` |
| `Limit` | Integer | Maximum number of streams to return. Default: 10. Valid range: 1–10000. |

**Response Structure:**

| Field | Type | Description |
|-|-|-|
| `DeliveryStreamNames` | Array of strings | The names of the Firehose streams. |
| `HasMoreDeliveryStreams` | Boolean | Indicates whether more streams are available beyond this page. |

### Sample Output

```
Hello, Amazon Data Firehose! Let's list your delivery streams:

 - my-s3-firehose-stream
 - analytics-log-stream
 - clickstream-delivery

Found 3 Firehose stream(s) in this region.
```

If no streams exist:

```
Hello, Amazon Data Firehose! Let's list your delivery streams:

No Firehose delivery streams found in this region.
```

### Test Requirements (Python)

The test file MUST be named `test_firehose_stubber.py` and use `botocore.stub.Stubber` exclusively. All tests are **unit tests only** — no integration tests, no real AWS calls, no AWS credentials required.

**Test file:** `test_firehose_stubber.py`

**Dependencies:** `requirements.txt` must include only pip-installable packages:
```
boto3
pytest
```

**Test pattern:**
1. Import `boto3` and `from botocore.stub import Stubber`.
2. Create a Firehose client via `boto3.client("firehose")`.
3. Create a `Stubber` on the client.
4. Use `add_response` or `add_client_error` for every API call.
5. Activate the Stubber before calling the function under test.
6. Assert expected outcomes.

**Required test cases:**

| Test Case | Description | Stubber Setup |
|-|-|-|
| `test_list_delivery_streams_with_streams` | Verifies that when streams exist, the function returns their names. | `add_response("list_delivery_streams", {"DeliveryStreamNames": ["stream-1", "stream-2"], "HasMoreDeliveryStreams": False})` |
| `test_list_delivery_streams_empty` | Verifies correct behavior when no streams exist. | `add_response("list_delivery_streams", {"DeliveryStreamNames": [], "HasMoreDeliveryStreams": False})` |
| `test_list_delivery_streams_has_more` | Verifies that the `HasMoreDeliveryStreams` flag is handled when `True`. | `add_response("list_delivery_streams", {"DeliveryStreamNames": ["stream-1"], "HasMoreDeliveryStreams": True})` |
| `test_list_delivery_streams_service_unavailable` | Verifies error handling for `ServiceUnavailableException`. | `add_client_error("list_delivery_streams", service_error_code="ServiceUnavailableException", service_message="The service is unavailable.")` |

**Constraints:**
- No `input()` calls.
- No `demo_tools`, `demo_helpers`, or non-pip modules.
- No integration tests, no `@pytest.mark.integ` markers.
- No real AWS resources created, used, or deleted.
- Every AWS API call in every test MUST have a corresponding Stubber `add_response` or `add_client_error`.
- Error tests MUST assert the specific exception type (e.g., `ServiceUnavailableException`), not generic `ClientError`.
- Tests MUST pass with `pytest test_*.py -v` in a Docker container with no AWS credentials.

## Errors

| Action | Exception | Handling |
|-|-|-|
| `ListDeliveryStreams` | `ServiceUnavailableException` | Notify the user that the Firehose service is temporarily unavailable and suggest retrying after a brief delay. |

## Metadata

| action / scenario | metadata file | metadata key |
|-|-|-|
| `ListDeliveryStreams` | firehose_metadata.yaml | firehose_Hello |
| `Firehose Hello` | firehose_metadata.yaml | firehose_Hello |
