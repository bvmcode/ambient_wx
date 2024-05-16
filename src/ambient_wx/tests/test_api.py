import pytest
import requests
import responses

from ambient_wx.api import ApiRequestHandler


def test_api_retries_success():
    root_url = "https://examplefoo.com"
    endpoint = "bar"
    url = f"{root_url}/{endpoint}"
    api = ApiRequestHandler(root_url)
    with responses.RequestsMock() as rsps:
        for _ in range(2):
            rsps.add(
                responses.GET,
                url,
                body="{}",
                status=429,
                content_type="application/json",
            )
        rsps.add(
            responses.GET,
            url,
            body="{}",
            status=200,
            content_type="application/json",
        )
        resp = api.get(endpoint)
        assert len(rsps.calls) == 3
        assert resp.status_code == 200


def test_api_exhaust_retries():
    root_url = "https://examplefoo.com"
    endpoint = "bar"
    url = f"{root_url}/{endpoint}"
    api = ApiRequestHandler(root_url)
    with responses.RequestsMock() as rsps:
        for _ in range(6):
            rsps.add(
                responses.GET,
                url,
                body="{}",
                status=429,
                content_type="application/json",
            )
        with pytest.raises(requests.exceptions.RetryError):
            api.get(endpoint)
