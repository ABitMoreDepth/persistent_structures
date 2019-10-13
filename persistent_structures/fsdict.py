"""Provides the FSDict module, implementing a MutableMapping interface atop the filesystem."""
import os
from collections.abc import MutableMapping
from typing import Iterator, Union


class FSDict(MutableMapping):
    """Implements a MutableMapping interface atop the filesystem.

    Provides a dictionary like entity which presents a directory of files to
    python via a dict interface.  Will return an FSDict to represent a
    directory, if one is requested.  Behaviour is undefined if presented with a
    symlink.
    """

    def __init__(self, directory: str = '.'):
        if os.path.isdir(directory):
            self.directory = directory
        else:
            raise ValueError("Directory must exist")

    def __setitem__(self, k: str, v: str) -> None:
        """Update the contents of a file if it exists, else raise a KeyError."""
        try:
            file_path = os.path.join(self.directory, k)
            with open(file_path, 'w') as file_handle:
                file_handle.write(v)
        except (OSError, IOError, ValueError, TypeError) as err:
            print("Encountered unexpected behaviour when storing key's value to disk.")
            raise KeyError("Unable to write file for {}".format(file_path)) from err

    def __getitem__(self, k: str) -> Union[str, bytes, 'FSDict']:
        """Retrieve the contents of a file (the dict's value), for the given key.

        Raise a KeyError if the file cannot be found.
        """
        try:
            target = os.path.join(self.directory, k)
            if os.path.isfile(target):
                with open(target) as file_handle:
                    return file_handle.read()

            elif os.path.isdir(target):
                return FSDict(target)

            else:
                raise KeyError(
                    "Unable to return file contents or a FSDict for {}".format(target),
                )

        except (ValueError, TypeError) as err:
            raise KeyError("{} doesn't exist.".format(target)) from err

    def __delitem__(self, k: str) -> None:
        """Delete the file specified by the provided key.

        (effectively removing the key and its value from the dict).  Raise
        KeyError if the file cannot be found.
        """
        try:
            os.remove(os.path.join(self.directory, k))
        except FileNotFoundError as err:
            raise KeyError from err

    def __len__(self) -> int:
        # Iterating through a generator of files here would be more memory
        # efficient, but scandir gives us a bunch of extra information that
        # isn't needed in this method, which would add uneeded CPU cost.
        return len(os.listdir(self.directory))

    def __iter__(self) -> Iterator[str]:
        return (
            file.name
            for file in os.scandir(self.directory)
            if any((os.path.isfile(file), os.path.isdir(file)))
        )
