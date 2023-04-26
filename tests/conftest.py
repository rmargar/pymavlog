from unittest.mock import Mock

import pytest
from pymavlink.DFReader import DFFormat
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from pymavlink.mavutil import mavserial


@pytest.fixture
def mavlink_message():
    def wrapper(
        msg_type: str = "TEST",
        content: dict = {"TimeUS": 123, "TestA": 22, "TestB": 0.121},
        timestamp: float = 123,
    ):
        message = Mock()
        message._timestamp = timestamp
        message.get_type.return_value = msg_type
        content["mavpackettype"] = msg_type
        message.to_dict.return_value = content
        return message

    return wrapper


@pytest.fixture
def mock_dfformat():
    def wrapper(name="TEST", columns=["TimeUS", "TestA", "TestB"], types=[int, int, float]):
        mock_dfformat = Mock(spec=DFFormat)
        mock_dfformat.name = name
        mock_dfformat.columns = columns
        mock_dfformat.msg_types = types
        return mock_dfformat

    return wrapper


@pytest.fixture
def mock_message_v2():
    def wrapper(
        name="TEST",
        columns=["TimeUS", "TestA", "TestB"],
        fieldtypes=["uint8_t", "uint32_t", "float"],
    ):
        mock_msg_v2 = Mock(spec=MAVLink_message)
        mock_msg_v2.msgname = name
        mock_msg_v2.get_fieldnames.return_value = columns
        mock_msg_v2.fieldtypes = fieldtypes
        return mock_msg_v2

    return wrapper


@pytest.fixture
def mock_mavutil(mock_dfformat):
    mock_mavutil = Mock()
    mock_mavserial = Mock(spec=mavserial)
    mock_mavutil.mavlink_connection.return_value = mock_mavserial
    mock_mavserial.name_to_id = {
        "TEST": 1,
        "GPS": 2,
        "FMT": 3,
        "MULT": 4,
        "PARM": 5,
        "IMU": 6,
    }
    mock_mavserial.formats = {
        1: mock_dfformat(
            name="TEST", columns=["TimeUS", "TestA", "TestB"], types=[int, float, float]
        ),
        2: mock_dfformat(name="GPS", columns=["TimeUS", "Lat", "Lon"], types=[int, float, float]),
        3: mock_dfformat(name="FMT", columns=["Foo", "Bar"], types=[int, float]),
        4: mock_dfformat(name="MULT", columns=["Foo", "Bar"], types=[int, float]),
        5: mock_dfformat(name="PARM", columns=["Foo", "Bar"], types=[int, float]),
        6: mock_dfformat(
            name="IMU",
            columns=["TimeUS", "GyrX", "GyrY", "AccX", "AccY"],
            types=[int, float, float, float, float],
        ),
    }
    return mock_mavutil


@pytest.fixture
def mock_mavutil_tlog(mock_message_v2):
    mock_mavutil = Mock()
    mock_mavserial = Mock(spec=mavserial)
    mock_mavutil.mavlink_connection.return_value = mock_mavserial
    mock_mavserial.name_to_id = {
        "RAW_IMU": 1,
        "GPS_STATUS": 2,
        "MAV": 3,
        "HEARBEAT": 4,
        "TEST": 5,
        "BATTERY_STATUS": 6,
    }

    mock_mavserial.messages = {
        "RAW_IMU": mock_message_v2(name="RAW_IMU"),
        "GPS_STATUS": mock_message_v2(name="GPS_STATUS"),
        "MAV": mock_message_v2(name="MAV"),
        "HEARBEAT": mock_message_v2(name="HEARBEAT"),
        "TEST": mock_message_v2(name="TEST"),
        "BATTERY_STATUS": mock_message_v2(name="BATTERY_STATUS"),
    }
    return mock_mavutil
