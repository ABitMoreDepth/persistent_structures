"""Provides the FSQueue module, implementing a Queue-like interface atop the filesystem."""

import os
from queue import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # This is annoying, and ugly as.  See
    # https://mypy.readthedocs.io/en/stable/common_issues.html
    #             using-classes-that-are-generic-in-stubs-but-not-at-runtime
    # for details.
    FSQUEUEBASE = Queue[str]  # pylint: disable = unsubscriptable-object
else:
    FSQUEUEBASE = Queue


class FSQueue(FSQUEUEBASE):  # pylint: disable = too-few-public-methods
    """Implements a Queue interface atop the filesystem.

    Provides a queue like entity which presents leverages a directory of files
    to store values in a queue.  The queue is lazy, and will evaluate only upon
    getting/putting from/to the queue, exchanging reduced memory consumption
    for increased CPU/IO cost.
    """

    def __init__(
            self,
            directory: str = '.',
            file_prefix: str = 'FSList-',
            maxsize: int = 0,
    ) -> None:
        if not os.path.isdir(directory):
            raise ValueError("Directory must exist")

        self.directory = directory
        self.file_prefix = file_prefix
        self.maxsize = maxsize

        super().__init__(maxsize)

    def _init(self, _) -> None:
        pass

    def _qsize(self) -> int:
        return len(os.listdir(self.directory))

    # Get an item from the queue
    def _get(self) -> str:
        items = os.listdir(self.directory)
        items.sort()
        target = os.path.join(self.directory, items[0])
        try:
            if os.path.isfile(target):
                content = ""
                with open(target) as file_handle:
                    content = file_handle.read()

                # Getting from the queue de-queues, so we should remove the
                # file here.
                os.remove(target)
                return content

            raise KeyError("Unable to return file contents for {}".format(target))

        except (ValueError, TypeError) as err:
            raise KeyError("{} doesn't exist.".format(target)) from err

    # Put a new item in the queue
    def _put(self, data: str) -> None:
        # Get the next available file_name for us to store the queue entry in.
        extant_items = os.listdir(self.directory)
        extant_items.sort()

        highest_name = '{}{}'.format(self.file_prefix, 1)
        for item in extant_items:
            print('current: {}, highest so far: {}'.format(item, highest_name))
            if item > highest_name:
                highest_name = item

        # Process the index out of the file name.
        suffix = highest_name.split(self.file_prefix)[-1]
        current_index = int(suffix) if suffix else 0

        new_name = '{}{}'.format(
            self.file_prefix,
            current_index + 1,
        )

        with open(os.path.join(self.directory, new_name), 'w') as file_handle:
            file_handle.write(data)
