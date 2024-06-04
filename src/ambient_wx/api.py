import logging

import requests
from requests.adapters import HTTPAdapter, Retry


class TimeoutHTTPAdapter(HTTPAdapter):
    default_timeout = (1, 10)

    def __init__(self, *args, **kwargs):
        self.timeout = self.default_timeout
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

    def __init__(self, root_url, **kwargs):
        if root_url.endswith("/"):
            root_url = root_url[:-1]
        self.root_url = root_url
        self.retry_total = kwargs.get("retry_total", 10)
        self.timeout = kwargs.get("timeout")

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

    def __message_handling(self, msg):
        logging.error(msg)
        raise SystemExit(msg)

    def get(self, endpoint=None, params=None):
        self.__get_session_with_retries()
        self.__build_url(endpoint)
        error_message = None
        try:
            logging.info(f"GET request: {self.url}")
            response = self.__session.get(self.url, params=params, verify=True)
            response.raise_for_status()
        except requests.exceptions.RetryError:
            error_message = "API GET request retries exhausted"
        except requests.exceptions.Timeout as e:
            error_message = f"API GET request timed out {e.response.status_code}"
        except requests.exceptions.ConnectionError as e:
            error_message = f"API GET connection error {e.response.status_code}"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                error_message = (
                    f"401 Unauthorized GET request {self.url} - "
                    "Check API Key and Application Key"
                )
            else:
                error_message = f"API Error {e.response.status_code}"
        except requests.exceptions.RequestException as e:
            error_message = f"Request error {e.response.status_code}"
        finally:
            if error_message is not None:
                self.__message_handling(error_message)

        self.__session.close()
        return response
