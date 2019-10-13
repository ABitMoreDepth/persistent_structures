"""Tests to cover the fsdict class."""

import os
from random import randint

import pytest

from persistent_structures.fsdict import FSDict


def test_delitem() -> None:
    """Verify Files are correctly deleted when deleting a key from the FSDict."""
    temp_file_path = os.path.join(os.path.curdir, 'test_delitem{}'.format(randint(0, 20)))

    with open(temp_file_path, 'w') as test_file_handle:
        test_file_handle.write('sample test file.')

    test_fsd = FSDict(os.path.curdir)

    del test_fsd[temp_file_path]

    assert os.path.isfile(temp_file_path) is False


def test_delitem_keyerror() -> None:
    """Verify we get a KeyError if we try to delete a key that is missing a matching file."""
    temp_file_path = os.path.join(
        os.path.curdir,
        '{}{}{}{}'.format(
            randint(0, 20),
            randint(0, 20),
            randint(0, 20),
            randint(0, 20),
        ),
    )

    # Make sure the file doesn't already exist otherwise we'll get a false negative.
    assert os.path.isfile(temp_file_path) is False

    test_fsd = FSDict(os.path.curdir)
    with pytest.raises(KeyError):
        del test_fsd[temp_file_path]


def test_iter() -> None:
    """Verify that __iter__ returns the appropriate file names (noddy test)."""
    test_fsd = FSDict(os.path.curdir)
    assert os.listdir(os.path.curdir) == [filename for filename in test_fsd]


def test_setitem() -> None:
    """Verify adding a key to FSDict creates a file with the appropriate value."""
    temp_file_path = 'test_setitem{}'.format(randint(0, 20))

    test_fsd = FSDict(os.path.curdir)
    test_fsd[temp_file_path] = 'sample text'

    with open(temp_file_path, 'r') as test_file_handle:
        assert test_file_handle.read() == 'sample text'

    os.remove(temp_file_path)


def test_setitem_fails() -> None:
    """Verify trying to create a file with an inappropriate name raises a KeyError."""
    test_fsd = FSDict(os.path.curdir)

    with pytest.raises(KeyError):
        test_fsd['\0'] = 'sample text'

    with pytest.raises(KeyError):
        test_fsd['/'] = 'sample text'


def test_ephemeral_initial_directory() -> None:
    """Verify we get a ValueError when instantiating FSDict with a non-extant directory."""
    with pytest.raises(ValueError):
        FSDict(
            '{}{}{}'.format(
                randint(0, 20),
                randint(0, 20),
                randint(0, 20),
            ),
        )


def test_getitem() -> None:
    """Verify retrieving the value for a key gives us the files content."""
    temp_file_path = os.path.join(os.path.curdir, 'test_delitem{}'.format(randint(0, 20)))

    file_content = "sample test file."
    with open(temp_file_path, 'w') as test_file_handle:
        test_file_handle.write(file_content)

    test_fsd = FSDict(os.path.curdir)

    assert file_content == test_fsd[temp_file_path]

    os.remove(temp_file_path)


def test_getitem_no_file() -> None:
    """Verify we get a KeyError when requesting a file that doesn't exist."""
    temp_file_path = os.path.join(
        os.path.curdir,
        '{}{}{}{}'.format(
            randint(0, 20),
            randint(0, 20),
            randint(0, 20),
            randint(0, 20),
        ),
    )

    # Make sure the file doesn't already exist otherwise we'll get a false negative.
    assert os.path.isfile(temp_file_path) is False

    test_fsd = FSDict(os.path.curdir)
    with pytest.raises(KeyError):
        test_fsd[temp_file_path]  # pylint: disable = pointless-statement


def test_getitem_invalid_name() -> None:
    """Verify we get a KeyError when requesting a file with an invalid name."""
    test_fsd = FSDict(os.path.curdir)

    with pytest.raises(KeyError):
        test_fsd['\0']  # pylint: disable = pointless-statement


def test_getiem_subdir() -> None:
    """Verify we get an FSDict instance back when requesting a directory."""
    test_fsd = FSDict(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))

    assert isinstance(test_fsd["tests"], FSDict)
