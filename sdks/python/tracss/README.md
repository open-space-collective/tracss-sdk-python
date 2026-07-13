# TraCSS Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=OpenSpaceCollective%2FPython)
[![pypi](https://img.shields.io/pypi/v/tracss)](https://pypi.python.org/pypi/tracss)

> [!IMPORTANT]
> **Code samples might show `token="YOUR_TOKEN"`. Do not use `token="YOUR_TOKEN"`.**
> The published SDK exports `TraCSS` (not `BaseTraCSS`), which handles
> Okta client-credentials auth automatically.
> You never construct or refresh a token yourself:
>
> ```python
> from tracss import TraCSS
>
> client = TraCSS(
>     client_id="…",       # or env TRACSS_CLIENT_ID
>     client_secret="…",   # or env TRACSS_CLIENT_SECRET
> )
>
> # Bulk Data
> for record in client.bulk_data.cdm.stream(...):
>     ...
>
> # Metadata - JSON is the default; no format= required
> results = client.metadata.cdm.list(...)
>
> # Subscriber
> topics = client.subscriber.topics.list()
> ```
>
> Tokens are fetched lazily on the first request and refreshed 30s before
> expiry. `AsyncTraCSS` is also available for async/await usage.
>
> ---
>
> **Metadata responses default to JSON.** The SDK ships
> `_MetadataWithJsonDefaults`, a subclass of the generated `MetadataClient`
> that silently injects `format="json"` on every `cdm`, `ocm`, and `tip_reports` list call.
> Without this, those metadata list endpoints return CCSDS KVN text by default that the Fern-generated
> response parser cannot handle. (The other metadata endpoints are JSON-only.) You do not need to pass `format=` at all for
> JSON since it is the default. To receive raw KVN, XML, or CSV instead, pass
> `format="KVN"` (or `"xml"`, `"csv"`) explicitly; the SDK catches the
> resulting `ApiError(status_code=200)` and returns `error.body` as a plain
> string (for Status OK responses only).


## Table of Contents

- [Documentation](#documentation)
- [Installation](#installation)
- [Reference](#reference)
- [Usage](#usage)
- [Environments](#environments)
- [Async Client](#async-client)
- [Exception Handling](#exception-handling)
- [Streaming](#streaming)
- [Advanced](#advanced)
  - [Access Raw Response Data](#access-raw-response-data)
  - [Retries](#retries)
  - [Timeouts](#timeouts)
  - [Custom Client](#custom-client)
- [Contributing](#contributing)

## Documentation

API reference documentation is available [here](https://open-space-collective.docs.buildwithfern.com).

## Installation

```sh
pip install tracss
```

## Reference

A full reference for this library is available [here](./reference.md).

## Usage

Instantiate and use the client with the following:

```python
from tracss import TraCSS

client = TraCSS(
    client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET",
)

client.bulk_data.cdm.stream(
    message_id="000043928_conj_000054603_2024329195621",
    tca="2024-314T07:41:39.411",
    creation_date="2024-09-04T18:37:01Z",
    message_for="IRIDIUM 161",
    screening_option="Covariance",
    screen_volume_shape="Box, Ellipsoid, Deep Space",
    object1type="Payload",
    object1international_designator="2019-002A",
    object1operator_organization="Iridium",
    object1ephemeris_name="NONE",
    object2type="Payload",
    object2international_designator="2019-002A",
    object2operator_organization="Iridium",
    object2ephemeris_name="NONE",
)
```

## Environments

This SDK allows you to configure different environments for API requests.

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    environment=TraCSSEnvironment.DEFAULT,
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API. Note that if you are constructing an Async httpx client class to pass into this client, use `httpx.AsyncClient()` instead of `httpx.Client()` (e.g. for the `httpx_client` parameter of this client).

```python
import asyncio

from tracss import AsyncTraCSS

client = AsyncTraCSS(
    client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET",
)


async def main() -> None:
    await client.bulk_data.cdm.stream(
        message_id="000043928_conj_000054603_2024329195621",
        tca="2024-314T07:41:39.411",
        creation_date="2024-09-04T18:37:01Z",
        message_for="IRIDIUM 161",
        screening_option="Covariance",
        screen_volume_shape="Box, Ellipsoid, Deep Space",
        object1type="Payload",
        object1international_designator="2019-002A",
        object1operator_organization="Iridium",
        object1ephemeris_name="NONE",
        object2type="Payload",
        object2international_designator="2019-002A",
        object2operator_organization="Iridium",
        object2ephemeris_name="NONE",
    )


asyncio.run(main())
```

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from tracss.core.api_error import ApiError

try:
    client.bulk_data.cdm.stream(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Streaming

The SDK supports streaming responses, as well, the response will be a generator that you can loop over.

```python
from tracss import TraCSS

client = TraCSS(
    client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET",
)

client.bulk_data.cdm.stream(
    message_id="000043928_conj_000054603_2024329195621",
    tca="2024-314T07:41:39.411",
    creation_date="2024-09-04T18:37:01Z",
    message_for="IRIDIUM 161",
    screening_option="Covariance",
    screen_volume_shape="Box, Ellipsoid, Deep Space",
    object1type="Payload",
    object1international_designator="2019-002A",
    object1operator_organization="Iridium",
    object1ephemeris_name="NONE",
    object2type="Payload",
    object2international_designator="2019-002A",
    object2operator_organization="Iridium",
    object2ephemeris_name="NONE",
)
```

## Advanced

### Access Raw Response Data

The SDK provides access to raw response data, including headers, through the `.with_raw_response` property.
The `.with_raw_response` property returns a "raw" client that can be used to access the `.headers` and `.data` attributes.

```python
from tracss import TraCSS

client = TraCSS(...)
response = client.bulk_data.cdm.with_raw_response.stream(...)
print(response.headers)  # access the response headers
print(response.status_code)  # access the response status code
print(response.data)  # access the underlying object
```

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retryable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

Which status codes are retried depends on the `retryStatusCodes` generator configuration:

**`legacy`** (current default): retries on
- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [409](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409) (Conflict)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#server_error_responses) (All server errors, including 500)

**`recommended`**: retries on
- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [409](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409) (Conflict)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [502](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502) (Bad Gateway)
- [503](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503) (Service Unavailable)
- [504](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504) (Gateway Timeout)

Use the `max_retries` request option to configure this behavior.

```python
client.bulk_data.cdm.stream(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python
from tracss import TraCSS

client = TraCSS(..., timeout=20.0)

# Override timeout for a specific method
client.bulk_data.cdm.stream(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
import httpx
from tracss import TraCSS

client = TraCSS(
    ...,
    httpx_client=httpx.Client(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
