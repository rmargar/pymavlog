class PyMavLogError(Exception):
    ...


class EmptyLogError(PyMavLogError):
    ...


class InvalidFormatError(PyMavLogError):
    ...
