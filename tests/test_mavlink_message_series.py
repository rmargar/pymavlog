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

    assert series.columns == ["timestamp", "TimeUS", "TestA", "TestB"]


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


def test_create_from_message(mock_message_v2):
    msg = mock_message_v2()
    series = MavLinkMessageSeries.from_message(msg)

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

    series.append_message(msg)

    assert len(series.fields["TimeUS"]) == 1
    assert series.fields["TimeUS"][0] == 123

    assert len(series.fields["TestA"]) == 1
    assert series.fields["TestA"][0] == 22

    assert len(series.fields["TestB"]) == 1
    assert series.fields["TestB"][0] == 0.121


def test_append_message_datetime(mavlink_message):
    msg_type = "TEST"
    content = {"TimeUS": 123, "TestA": 22, "TestB": 0.121}
    msg = mavlink_message(msg_type, content, 123)

    series = MavLinkMessageSeries(
        name=msg_type,
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
        column_alias={"TimeUS": "time_from_start"},
        convert_to_datetime=True,
    )

    series.append_message(msg)

    assert len(series.fields["time_from_start"]) == 1
    assert series.fields["time_from_start"][0] == 123

    assert series.fields["timestamp"][0] == datetime.fromtimestamp(123)


def test_append_message_raises_value_error(mavlink_message):
    msg_type = "FOO"
    content = {"FOO": 123, "BAR": 22}
    msg = mavlink_message(msg_type, content)
    series = MavLinkMessageSeries(
        name="TEST",
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
        column_alias={"TimeUS": "time_from_start"},
        convert_to_datetime=True,
    )

    with pytest.raises(ValueError):
        series.append_message(msg)


def test_getitem(mavlink_message):
    msg_type = "TEST"

    msg_1 = mavlink_message(msg_type, {"TimeUS": 123, "TestA": 22, "TestB": 0.121})
    msg_2 = mavlink_message(msg_type, {"TimeUS": 124, "TestA": 23, "TestB": 0.122})

    series = MavLinkMessageSeries(
        name=msg_type,
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
    )

    series.append_message(msg_1)
    series.append_message(msg_2)

    np.testing.assert_array_equal(series["TimeUS"], np.array([123, 124]))
    np.testing.assert_array_equal(series["TestA"], np.array([22, 23]))
    np.testing.assert_array_equal(series["TestB"], np.array([0.121, 0.122]))


@pytest.mark.parametrize(
    "rate,expected_timestamps",
    [
        (2, [123.1, 124.5, 125.1]),
        (None, [123.1, 123.3, 124.5, 124.6, 125.1]),
    ],
)
def test_reduce_rate(mavlink_message, rate, expected_timestamps):
    msg_type = "TEST"

    msg_1 = mavlink_message(
        msg_type, {"TimeUS": 123.1, "TestA": 22, "TestB": 0.121}, timestamp=123.1
    )
    msg_2 = mavlink_message(
        msg_type, {"TimeUS": 123.3, "TestA": 23, "TestB": 0.122}, timestamp=123.3
    )
    msg_3 = mavlink_message(
        msg_type, {"TimeUS": 124.5, "TestA": 24, "TestB": 0.123}, timestamp=124.5
    )
    msg_4 = mavlink_message(
        msg_type, {"TimeUS": 124.6, "TestA": 25, "TestB": 0.124}, timestamp=124.6
    )
    msg_5 = mavlink_message(
        msg_type, {"TimeUS": 125.1, "TestA": 26, "TestB": 0.125}, timestamp=125.1
    )
    msg_6 = mavlink_message(
        msg_type, {"TimeUS": 125.1, "TestA": 26, "TestB": 0.125}, timestamp=None
    )

    series = MavLinkMessageSeries(
        name=msg_type,
        columns=["TimeUS", "TestA", "TestB"],
        types=[int, int, float],
        max_rate_hz=rate,
    )

    series.append_message(msg_1)
    series.append_message(msg_2)
    series.append_message(msg_3)
    series.append_message(msg_4)
    series.append_message(msg_5)
    series.append_message(msg_6)

    assert len(series.fields["timestamp"]) == len(expected_timestamps)
    assert all(s in expected_timestamps for s in series.fields["timestamp"])


def test_series_raises_value_error_invalid_rate():
    with pytest.raises(ValueError):
        MavLinkMessageSeries(
            name="TEST",
            columns=["TimeUS", "TestA", "TestB"],
            types=[int, int, float],
            max_rate_hz="foo",
        )


def test_series_does_not_reduce_parm(mavlink_message):
    msg_type = "PARM"

    msg_1 = mavlink_message(
        msg_type, {"TimeUS": 123.1, "TestA": 22, "TestB": 0.121}, timestamp=123.1
    )
    msg_2 = mavlink_message(
        msg_type, {"TimeUS": 123.3, "TestA": 23, "TestB": 0.122}, timestamp=123.3
    )
    msg_3 = mavlink_message(
        msg_type, {"TimeUS": 123.3, "TestA": 23, "TestB": 0.122}, timestamp=123.35
    )

    series = MavLinkMessageSeries(
        name=msg_type, columns=["TimeUS", "TestA", "TestB"], types=[int, int, float], max_rate_hz=1
    )

    series.append_message(msg_1)
    series.append_message(msg_2)
    series.append_message(msg_3)

    assert len(series.fields["timestamp"]) == 3
