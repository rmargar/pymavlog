import pytest

from pymavlog import EmptyLogError, MavLinkMessageSeries, MavTLog, core


def test_types(mavlink_message, mock_mavutil_tlog, monkeypatch):
    monkeypatch.setattr(core, "mavutil", mock_mavutil_tlog)

    tlog = MavTLog(filepath="foo/bar.bin")

    test_msg = tlog.get("TEST")

    assert isinstance(test_msg, MavLinkMessageSeries)
    assert tlog.message_count == 0
    assert len(tlog.types) == 5

    assert "HEARTBEAT" not in tlog.parsed_data.keys()
    assert len(tlog.parsed_data) == 5


def test_types_empty_error(mavlink_message, mock_mavutil_tlog, monkeypatch):
    monkeypatch.setattr(core, "mavutil", mock_mavutil_tlog)
    with pytest.raises(EmptyLogError):
        MavTLog(filepath="foo/bar.bin", types=[])
