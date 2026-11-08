from copy import deepcopy
from queue import Empty, Full, Queue


class CommandOutbox:

    def __init__(
        self,
        maxsize=1000
    ):

        self._queue = Queue(
            maxsize=maxsize
        )


    def put(
        self,
        payload
    ):

        try:

            self._queue.put_nowait(
                deepcopy(payload)
            )

            return True

        except Full:

            return False


    def pull(
        self,
        limit=100
    ):

        try:

            limit = int(limit)

        except Exception:

            limit = 100


        limit = max(
            1,
            min(
                limit,
                1000
            )
        )


        result = []


        for _ in range(limit):

            try:

                result.append(
                    self._queue.get_nowait()
                )

            except Empty:

                break


        return result


    def qsize(
        self
    ):

        return self._queue.qsize()
