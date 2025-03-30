import io
import re
from abc import ABC, abstractmethod
from typing import Optional, Any, Union


class ServerSentEventABC(ABC):
    """
    Abstract base class to format data for Server-Sent Events (SSE).
    """

    @abstractmethod
    def __init__(
        self,
        data: Optional[Any] = None,
        *,
        event: Optional[Any] = None,
        id: Optional[Any] = None,
        retry: Optional[int] = None,
        comment: Optional[Any] = None,
        sep: Optional[Any] = None,
    ) -> None:
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry
        self.comment = comment
        self._sep = sep if sep is not None else self.DEFAULT_SEPARATOR

    def _encode(self, write) -> None:
        if self.comment is not None:
            for chunk in self._LINE_SEP_EXPR.split(self.comment):
                write(self.TAG_COMMENT)
                write(chunk)
                write(self._sep)

        if self.id is not None:
            # Clean newlines in the event id
            write(self.TAG_ID)
            write(self._LINE_SEP_EXPR.sub(b"", self.id))
            write(self._sep)

        if self.event is not None:
            # Clean newlines in the event name
            write(self.TAG_EVENT)
            write(self._LINE_SEP_EXPR.sub(b"", self.event))
            write(self._sep)

        if self.data is not None:
            # Break multi-line data into multiple data: lines
            for chunk in self._LINE_SEP_EXPR.split(self.data):
                write(self.TAG_DATA)
                write(chunk)
                write(self._sep)

        if self.retry is not None:
            if not isinstance(self.retry, int):
                raise TypeError("retry argument must be int")
            write(self.TAG_RETRY)
            write(str(self.retry).encode("utf-8"))
            write(self._sep)

        write(self._sep)

    @abstractmethod
    def encode(self) -> bytes:
        return b""


class ServerSentEvent(ServerSentEventABC):
    """
    Helper class to format data for Server-Sent Events (SSE).
    """

    _LINE_SEP_EXPR = re.compile(r"\r\n|\r|\n")
    DEFAULT_SEPARATOR = "\r\n"

    TAG_COMMENT = ": "
    TAG_ID = "id: "
    TAG_EVENT = "event: "
    TAG_DATA = "data: "
    TAG_RETRY = "retry: "

    def __init__(
        self,
        data: Optional[Any] = None,
        *,
        event: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None,
        comment: Optional[str] = None,
        sep: Optional[str] = None,
    ) -> None:
        self.data = str(data)
        self.event = event
        self.id = id
        self.retry = retry
        self.comment = comment
        self._sep = sep if sep is not None else self.DEFAULT_SEPARATOR

    def encode(self) -> bytes:
        buffer = io.StringIO()
        write = buffer.write
        self._encode(write)
        return buffer.getvalue().encode("utf-8")


class ServerSentEventBytes(ServerSentEventABC):
    """
    Helper class to format bytes data for Server-Sent Events (SSE).
    """

    _LINE_SEP_EXPR = re.compile(br"\r\n|\r|\n")
    DEFAULT_SEPARATOR = b"\n"

    TAG_COMMENT = b": "
    TAG_ID = b"id: "
    TAG_EVENT = b"event: "
    TAG_DATA = b"data: "
    TAG_RETRY = b"retry: "

    def __init__(
        self,
        data: Optional[bytes] = None,
        *,
        event: Optional[bytes] = None,
        id: Optional[bytes] = None,
        retry: Optional[int] = None,
        comment: Optional[bytes] = None,
        sep: Optional[bytes] = None,
    ) -> None:
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry
        self.comment = comment
        self._sep = sep if sep is not None else self.DEFAULT_SEPARATOR

    def encode(self) -> bytes:
        buffer = io.BytesIO()
        self.encode(buffer.write)
        return buffer.getvalue()


def ensure_bytes(data: Union[bytes, dict, ServerSentEventABC, Any], sep: str) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, ServerSentEventABC):
        return data.encode()
    if isinstance(data, dict):
        data["sep"] = sep
        return ServerSentEvent(**data).encode()
    return ServerSentEvent(data, sep=sep).encode()
