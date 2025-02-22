# Uhomepy

Uhomepy is a simple Python API wrapper for the [U home OpenAPI](https://developer.uhomelabs.com/hc/en-us/sections/39589678120985-Developer-Documentation). This library provides an abstract base class `UhomeOpenAPI` to interact with the Uhome API. It includes methods to authenticate and make requests to the API, such as discovering, querying, locking, and unlocking devices.

## Configuration

To use the Uhome API, you will need a `client_id`, a `client_secret`, and a `RedirectURI`.

> [!TIP]
> Install and set up the U home app before starting the following steps.

1. Contact [U-tec Customer Service](https://support.u-tec.com/hc/en-us/requests/new) to request a Developer Account. Once your Developer Account is set up, the Developer Console menu option will appear in your U home app.
2. In the Developer Console, note the `client_id` and `client_secret`.
3. In the Developer Console, add a `RedirectUri`. For the `dump_devices` example included in this project, use any non-public URI (e.g., https://localhost:8080).

## Usage

### Implementing the UhomeOpenAPI

To use the UhomeOpenAPI, you need to create a concrete implementation of the abstract class which implements the `async_get_access_token` method.

### Example Script

An example script `dump_devices.py` is provided in the `examples` directory. This script demonstrates how to use the Uhome API to authenticate a user, retrieve an access token, and dump the list of devices associated with the user.

To run the example script, use the following command:

```sh
python examples/dump_devices.py
```

When running the example script, you will need to authenticate and approve access. You will be redirected to the `RedirectUri`, which will not load. However, you only need to copy the URI from the address bar of your browser for the final step of the script.

## Limitations

The U home OpenAPI supports SmartLock, SmartPlug, SmartSwitch and Light devices. This library will discover all of these devices types but only supports interacting with SmartLocks.