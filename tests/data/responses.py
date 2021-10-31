import abc


class MockResponse(abc.ABC):
    @property
    @abc.abstractmethod
    def status_code(self):
        raise NotImplementedError(
            "Required HTTP CODE implementation for responses"
        )

    @staticmethod
    @abc.abstractmethod
    def json():
        raise NotImplementedError("Required json implementation for responses")
