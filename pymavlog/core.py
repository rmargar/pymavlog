import typing as t
from datetime import datetime

import numpy as np
from pymavlink import mavutil
from pymavlink.DFReader import DFFormat, DFMessage

from .errors import EmptyLogError, InvalidFormatError


class MavLinkMessageSeries(object):
    """
    Class that represents a timeseries of MavLink messages
    """

    def __init__(
        self,
        name: str,
        columns: t.List[str],
        types: t.List[type],
        column_alias: t.Dict[str, str] = {},
        msg_id: int = 1,
        convert_to_datetime: bool = False,
    ) -> None:
        self.name = name
        self.id = msg_id
        self._to_datetime = convert_to_datetime
        self._column_alias = column_alias

        if len(columns) != len(types):
            raise InvalidFormatError("columns and types must have the same length")

        self._columns = columns
        self._types = types
        self._fields: t.Dict[str, t.List[datetime | int | float]] = {}
        self.__set_series()

    def __set_series(
        self,
    ):
        for idx, c in enumerate(self._columns):
            if c == "TimeUS":
                self._types[idx] = datetime
            self._fields[self._column_alias.get(c, c)] = []

    @classmethod
    def from_df_format(
        cls,
        fmt: DFFormat,
        column_alias: t.Dict[str, str] = {},
        msg_id: int = 1,
        convert_to_datetime: bool = False,
    ):
        return cls(
            name=fmt.name,
            columns=fmt.columns,
            types=fmt.msg_types,
            column_alias=column_alias,
            msg_id=msg_id,
            convert_to_datetime=convert_to_datetime,
        )

    @property
    def fields(self) -> t.Dict[str, np.ndarray]:
        """
        The timeseries fields as a numpy array
        """
        fields_np = {}
        for idx, c in enumerate(self._columns):
            fields_np[self._column_alias.get(c, c)] = np.array(
                object=self._fields[self._column_alias.get(c, c)],
                dtype=self._types[idx],
            )
        return fields_np

    @property
    def raw_fields(self) -> t.Dict[str, list]:
        """
        The timeseries fields as a python list
        """
        return self._fields

    def append_message(self, message: dict) -> None:
        msg_type = message["mavpackettype"]

        if msg_type != self.name:
            raise ValueError(f"Invalid message type, got {msg_type}, expected {self.name}")

        message.pop("mavpackettype")

        for k, v in message.items():
            if k == "TimeUS" and self._to_datetime:
                self._fields[self._column_alias.get(k, k)].append(datetime.fromtimestamp(v))
            else:
                self._fields[self._column_alias.get(k, k)].append(v)


class MavLog(object):
    def __init__(
        self,
        filepath: str,
        messages_to_ignore: t.List[str] = ["FMT", "FMTU"],
        types: t.List[str] = None,
        to_datetime: bool = False,
        map_columns: t.Dict[str, str] = {},
    ):
        self._messages_ignore = messages_to_ignore
        self._mlog: mavutil.mavserial = mavutil.mavlink_connection(filepath)

        self._parsed_data: t.Dict[str, MavLinkMessageSeries] = {}
        self._start_timestamp = 0
        self._end_timestamp = 0
        self._msg_count = 0
        self._to_datetime = to_datetime
        self._map_columns = map_columns
        self._start_timestamp = None
        self._end_timestamp = None

        self.__set_parsed_data(types)

    @property
    def parsed_data(self) -> t.Dict[str, MavLinkMessageSeries]:
        return self._parsed_data

    @property
    def message_count(self) -> int:
        return self._msg_count

    @property
    def types(self) -> t.List[str]:
        return self._types

    @property
    def start_timestamp(self) -> t.Union[float, datetime]:
        if self._to_datetime:
            return datetime.fromtimestamp(self._start_timestamp)
        else:
            return self._start_timestamp

    @property
    def end_timestamp(self) -> t.Union[float, datetime]:
        if self._to_datetime:
            return datetime.fromtimestamp(self._end_timestamp)
        else:
            return self._end_timestamp

    def __set_parsed_data(self, types: t.List[str]):
        self._types = []
        for name, msg_id in self._mlog.name_to_id.items():
            fmt = self._mlog.formats[msg_id]

            msg_not_in_types = (types is not None) and (name not in types)
            ignore_type = (name in self._messages_ignore) or msg_not_in_types
            if ignore_type:
                continue

            self._types.append(fmt.name)
            self._parsed_data[name] = MavLinkMessageSeries.from_df_format(
                fmt, self._map_columns, msg_id, self._to_datetime
            )
        if not self._types:
            raise EmptyLogError("The log contains no message types")

    def parse(self):
        """
        Parses the log file in-memory
        """
        message: DFMessage

        while True:
            message = self._mlog.recv_match(type=self._types)

            if message is None:
                break

            message: DFMessage

            msg_dict = message.to_dict()

            self._parsed_data[message.get_type()].append_message(msg_dict)

            try:
                self._end_timestamp = msg_dict["TimeUS"]
                if self._msg_count == 0 or not self._start_timestamp:
                    self._start_timestamp = msg_dict["TimeUS"]
            except KeyError:
                pass

            self._msg_count += 1

    def get(self, key: str):
        """
        Returns a MavLinkMessageSeries object for the given key

        ----
        Parameters
        ----

            key (str): The name of the series

        ----
        Returns
        ----
            MavLinkMessageSeries
        """
        return self._parsed_data.get(key)
