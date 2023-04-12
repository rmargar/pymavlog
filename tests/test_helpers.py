import pytest
from pymavlog.helpers import to_snake_case


@pytest.mark.parametrize(
    ["value", "expected"],
    [("ToSnakeCase", "to_snake_case"), ("toDo", "to_do")],
)
def test_to_snake_case(value, expected):
    assert to_snake_case(value) == expected
