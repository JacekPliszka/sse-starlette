import io
import re
from typing import Optional, Any, Union


class ServerSentEvent:
    """
    Helper class to format data for Server-Sent Events (SSE).
    """

    _LINE_SEP_EXPR = re.compile(r"\r\n|\r|\n")
    DEFAULT_SEPARATOR = "\r\n"

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
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry
        self.comment = comment
        self._sep = sep if sep is not None else self.DEFAULT_SEPARATOR

    def encode(self) -> bytes:
        buffer = io.StringIO()
        if self.comment is not None:
            for chunk in self._LINE_SEP_EXPR.split(str(self.comment)):
                buffer.write(f": {chunk}{self._sep}")

        if self.id is not None:
            # Clean newlines in the event id
            buffer.write("id: " + self._LINE_SEP_EXPR.sub("", self.id) + self._sep)

        if self.event is not None:
            # Clean newlines in the event name
            buffer.write(
                "event: " + self._LINE_SEP_EXPR.sub("", self.event) + self._sep
            )

        if self.data is not None:
            # Break multi-line data into multiple data: lines
            for chunk in self._LINE_SEP_EXPR.split(str(self.data)):
                buffer.write(f"data: {chunk}{self._sep}")

        if self.retry is not None:
            if not isinstance(self.retry, int):
                raise TypeError("retry argument must be int")
            buffer.write(f"retry: {self.retry}{self._sep}")

        buffer.write(self._sep)
        return buffer.getvalue().encode("utf-8")


_LINE_SEP_EXPR_BYTES = re.compile(rb"\r\n|\r|\n")
DEFAULT_SEPARATOR_BYTES = b"\r\n"


def event_from_bytes(
    self,
    data: Optional[bytes] = None,
    *,
    event: Optional[bytes] = None,
    id: Optional[bytes] = None,  # noqa: W0622
    retry: Optional[int] = None,
    comment: Optional[bytes] = None,
    sep: Optional[bytes] = None,
) -> bytes:
    """
    Format a message for Server-Sent Events (SSE) from bytes data.

    :param data: The data to send.
    :param event: The event name.
    :param id: The event ID.
    :param retry: The retry time in milliseconds.
    :param comment: A comment to send.
    :param sep: The separator to use between lines.
    :return: The formatted message as bytes.
    """

    buffer = io.BytesIO()
    write = buffer.write

    _sep = sep if sep is not None else DEFAULT_SEPARATOR_BYTES

    if comment is not None:
        for chunk in _LINE_SEP_EXPR_BYTES.split(comment):
            write(b": ")
            write(chunk)
            write(_sep)

    if id is not None:
        # Clean newlines in the event id
        write(b"id: ")
        write(_LINE_SEP_EXPR_BYTES.sub(b"", id))
        write(_sep)

    if event is not None:
        # Clean newlines in the event name
        write(b"event: ")
        write(_LINE_SEP_EXPR_BYTES.sub(b"", event))
        write(_sep)

    if data is not None:
        # Break multi-line data into multiple data: lines
        for chunk in _LINE_SEP_EXPR_BYTES.split(data):
            write(b"data: ")
            write(chunk)
            write(_sep)

    if retry is not None:
        if not isinstance(retry, int):
            raise TypeError("retry argument must be int")
        write(b"retry: ")
        write(str(retry).encode("utf-8"))
        write(_sep)

    write(_sep)
    return buffer.getvalue()


def ensure_bytes(data: Union[bytes, dict, ServerSentEvent, Any], sep: str) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, ServerSentEvent):
        return data.encode()
    if isinstance(data, dict):
        data["sep"] = sep
        return ServerSentEvent(**data).encode()
    return ServerSentEvent(str(data), sep=sep).encode()
