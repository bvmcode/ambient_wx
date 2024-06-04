import pytest
import requests
import responses

from ambient_wx.api import ApiRequestHandler


class TestApiRequestHandler:

    def setup_method(self, url):
        self.root_url = "https://examplefoo.com"
        self.endpoint = "bar"
        self.url = f"{self.root_url}/{self.endpoint}"

    def test_api_retries_success(self):
        api = ApiRequestHandler(self.root_url)
        with responses.RequestsMock() as rsps:
            for _ in range(2):
                rsps.add(
                    responses.GET,
                    self.url,
                    body="{}",
                    status=429,
                    content_type="application/json",
                )
            rsps.add(
                responses.GET,
                self.url,
                body="{}",
                status=200,
                content_type="application/json",
            )
            resp = api.get(self.endpoint)
            assert len(rsps.calls) == 3
            assert resp.status_code == 200

    def test_api_exhaust_retries(self):
        api = ApiRequestHandler(self.root_url)
        with responses.RequestsMock() as rsps:
            for _ in range(6):
                rsps.add(
                    responses.GET, self.url, body="{}", status=429, content_type="application/json"
                )
            with pytest.raises((requests.exceptions.RetryError, SystemExit)):
                api.get(self.endpoint)
