from unittest.mock import Mock

import pytest
from pymavlink.DFReader import DFFormat
from pymavlink.mavutil import mavserial


@pytest.fixture
def mavlink_message():
    def wrapper(
        msg_type: str = "TEST",
        content: dict = {"TimeUS": 123, "TestA": 22, "TestB": 0.121},
    ):
        message = Mock()
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
