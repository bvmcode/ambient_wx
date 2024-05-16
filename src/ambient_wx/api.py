import logging

import requests
from requests.adapters import HTTPAdapter, Retry


class TimeoutHTTPAdapter(HTTPAdapter):
    default_timeout = 30

    def __init__(self, *args, **kwargs):
        self.timeout = self.default_timeout
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class LogRetry(Retry):
    def __init__(self, *args, **kwargs):
        if "history" in kwargs:
            retry_number = len(kwargs["history"])
            last_status = kwargs["history"][-1].status
            message = f"Retry {retry_number}: status code {last_status}"
            logging.info(message)
        super().__init__(*args, **kwargs)


class ApiRequestHandler:
    retry_status_codes = [429, 500, 502, 503, 504]
    backoff_factor = 0.1
    retry_total = 5

    def __init__(self, root_url):
        if root_url.endswith("/"):
            root_url = root_url[:-1]
        self.root_url = root_url

    def __repr__(self):
        return f"ApiRequestHandler({self.root_url})"

    def __get_session_with_retries(self):
        self.__session = requests.Session()
        retries = LogRetry(
            total=self.retry_total,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.retry_status_codes,
        )
        self.__session.mount(self.root_url, TimeoutHTTPAdapter(max_retries=retries))

    def __build_url(self, endpoint):
        if endpoint is not None:
            self.url = f"{self.root_url}/{endpoint}"
        else:
            self.url = self.root_url

    def get(self, endpoint=None, params=None):
        self.__get_session_with_retries()
        self.__build_url(endpoint)
        try:
            logging.info(f"GET request: {self.url}")
            response = self.__session.get(self.url, params=params, verify=True)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                message = (
                    f"401 Unauthorized GET request {self.url} - "
                    "Check API Key and Application Key"
                )
            else:
                message = f"API Error: {e.response.reason} ({e.response.status_code})"
            logging.error(message)
            raise e
        except requests.exceptions.RetryError as e:
            message = "Retries exhausted"
            logging.error("API GET request retries exhausted")
            raise e
        self.__session.close()
        return response
