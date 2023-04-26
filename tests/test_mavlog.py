from datetime import datetime

import pytest

from pymavlog import MavLinkMessageSeries, MavLog, core
from pymavlog.errors import EmptyLogError


def test_types(mavlink_message, mock_mavutil, monkeypatch):
    monkeypatch.setattr(core, "mavutil", mock_mavutil)

    mlog = MavLog(filepath="foo/bar.bin")

    test_msg = mlog.get("TEST")

    assert isinstance(test_msg, MavLinkMessageSeries)
    assert mlog.message_count == 0
    assert len(mlog.types) == 5

    assert "FMT" not in mlog.parsed_data.keys()
    assert len(mlog.parsed_data) == 5


def test_mavlog_defined_types(mock_mavutil, monkeypatch):
    monkeypatch.setattr(core, "mavutil", mock_mavutil)

    mlog = MavLog(filepath="foo/bar.bin", types="IMU")

    test_1 = mlog.get("IMU")

    assert isinstance(test_1, MavLinkMessageSeries)
    assert mlog.message_count == 0
    assert len(mlog.types) == 1
    assert len(mlog.parsed_data) == 1


def test_mavlog_defined_types_raises_error(mavlink_message, mock_mavutil, monkeypatch):
    monkeypatch.setattr(core, "mavutil", mock_mavutil)
    with pytest.raises(EmptyLogError):
        MavLog(filepath="foo/bar.bin", types="FOO")


def test_parse(mavlink_message, mock_mavutil, monkeypatch):
    mock_mavutil.mavlink_connection().recv_msg.side_effect = [
        mavlink_message(),
        mavlink_message(msg_type="GPS", content={"TimeUS": 222, "Lat": 0.22, "Lon": 0.121}),
        mavlink_message(msg_type="UNKNOWNTYPE", content={"TimeUS": 222, "X": 0.22, "Y": 0.121}),
        None,
    ]

    monkeypatch.setattr(core, "mavutil", mock_mavutil)

    mlog = MavLog(filepath="foo/bar.bin")
    mlog.parse()

    assert mlog.start_timestamp == 123
    assert mlog.end_timestamp == 222

    assert mlog.message_count == 2


def test_parse_with_timestamp(mavlink_message, mock_mavutil, monkeypatch):
    mock_mavutil.mavlink_connection().recv_msg.side_effect = [
        mavlink_message(msg_type="MULT", content={"Foo": 1, "Bar": 0.121}),
        mavlink_message(),
        mavlink_message(msg_type="GPS", content={"TimeUS": 222, "Lat": 0.22, "Lon": 0.121}),
        None,
    ]

    monkeypatch.setattr(core, "mavutil", mock_mavutil)

    mlog = MavLog(filepath="foo/bar.bin", to_datetime=True)
    mlog.parse()

    assert mlog.start_timestamp == datetime.fromtimestamp(123)
    assert mlog.end_timestamp == datetime.fromtimestamp(222)

    assert mlog.message_count == 3
