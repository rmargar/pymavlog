from datetime import datetime

import numpy as np
import pytest
from pymavlog import MavLinkMessageSeries
from pymavlog.errors import InvalidFormatError


def test_create():
    series = MavLinkMessageSeries(
        name="TEST",
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
    )
    assert isinstance(series.fields["TimeUS"], np.ndarray)
    assert isinstance(series.fields["TestA"], np.ndarray)
    assert isinstance(series.fields["TestB"], np.ndarray)

    assert len(series.fields["TimeUS"]) == 0
    assert len(series.fields["TestA"]) == 0
    assert len(series.fields["TestB"]) == 0

    assert isinstance(series.raw_fields["TimeUS"], list)
    assert isinstance(series.raw_fields["TestA"], list)
    assert isinstance(series.raw_fields["TestB"], list)


def test_create_from_mavlink_format(mock_dfformat):
    dfformat = mock_dfformat()
    series = MavLinkMessageSeries.from_df_format(fmt=dfformat)

    assert isinstance(series.fields["TimeUS"], np.ndarray)
    assert isinstance(series.fields["TestA"], np.ndarray)
    assert isinstance(series.fields["TestB"], np.ndarray)

    assert len(series.fields["TimeUS"]) == 0
    assert len(series.fields["TestA"]) == 0
    assert len(series.fields["TestB"]) == 0

    assert isinstance(series.raw_fields["TimeUS"], list)
    assert isinstance(series.raw_fields["TestA"], list)
    assert isinstance(series.raw_fields["TestB"], list)


def test_create_with_alias(mock_dfformat):
    dfformat = mock_dfformat()
    series = MavLinkMessageSeries.from_df_format(fmt=dfformat, column_alias={"TestA": "other_name"})

    assert isinstance(series.fields["other_name"], np.ndarray)
    assert isinstance(series.raw_fields["other_name"], list)


def test_create_raises_invalid_config():
    with pytest.raises(InvalidFormatError):
        MavLinkMessageSeries(
            name="TEST",
            columns=["TimeUS", "TestA", "TestB"],
            types=[int, int],
        )


def test_append_message(mavlink_message):
    msg_type = "TEST"
    content = {"TimeUS": 123, "TestA": 22, "TestB": 0.121}
    msg = mavlink_message(msg_type, content)

    series = MavLinkMessageSeries(
        name=msg_type,
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
    )

    series.append_message(msg.to_dict())

    assert len(series.fields["TimeUS"]) == 1
    assert series.fields["TimeUS"][0] == 123

    assert len(series.fields["TestA"]) == 1
    assert series.fields["TestA"][0] == 22

    assert len(series.fields["TestB"]) == 1
    assert series.fields["TestB"][0] == 0.121


def test_append_message_datetime(mavlink_message):
    msg_type = "TEST"
    content = {"TimeUS": 123, "TestA": 22, "TestB": 0.121}
    msg = mavlink_message(msg_type, content)

    series = MavLinkMessageSeries(
        name=msg_type,
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
        column_alias={"TimeUS": "timestamp"},
        convert_to_datetime=True,
    )

    series.append_message(msg.to_dict())

    assert len(series.fields["timestamp"]) == 1
    assert series.fields["timestamp"][0] == datetime.fromtimestamp(123)


def test_append_message_raises_value_error(mavlink_message):
    msg_type = "FOO"
    content = {"FOO": 123, "BAR": 22}
    msg = mavlink_message(msg_type, content)
    series = MavLinkMessageSeries(
        name="TEST",
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
        column_alias={"TimeUS": "timestamp"},
        convert_to_datetime=True,
    )

    with pytest.raises(ValueError):
        series.append_message(msg.to_dict())
