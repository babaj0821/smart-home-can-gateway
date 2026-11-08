import builtins
from queue import Queue, Empty, Full
from threading import RLock
from typing import Dict

from .events import BusEvent


class Subscription:
    """
    Represents one subscriber to one Event Bus topic.

    Every subscriber has its own queue.

    Therefore multiple subscribers can receive the same event
    without consuming each other's messages.
    """

    def __init__(
        self,
        topic: str,
        subscriber_id: str,
        maxsize: int = 1000,
        overflow_policy: str = "drop_oldest"
    ):
        self.topic = topic
        self.subscriber_id = subscriber_id

        self._queue = Queue(maxsize=maxsize)

        self._overflow_policy = overflow_policy

    def get(self, timeout=None) -> BusEvent:
        """
        Wait for the next event.

        timeout=None:
            wait forever

        timeout=1:
            wait maximum 1 second
        """

        return self._queue.get(timeout=timeout)

    def get_nowait(self) -> BusEvent:
        """
        Return immediately.

        Raises queue.Empty if there is no event.
        """

        return self._queue.get_nowait()

    def empty(self) -> bool:
        return self._queue.empty()

    def qsize(self) -> int:
        return self._queue.qsize()

    def _push(self, event: BusEvent) -> bool:
        """
        Internal EventBus method.

        Never blocks the publisher.
        """

        try:
            self._queue.put_nowait(event)
            return True

        except Full:
            pass

        # Queue is full.

        if self._overflow_policy != "drop_oldest":
            return False

        # Drop the oldest event so the newest state can enter.

        try:
            self._queue.get_nowait()

        except Empty:
            pass

        try:
            self._queue.put_nowait(event)
            return True

        except Full:
            return False


class EventBus:
    """
    Thread-safe in-process Publish / Subscribe Event Bus.

    The EventBus does NOT execute subscriber callbacks.

    publish():
        only inserts events into subscriber queues
        and returns immediately.

    This is important because CAN telemetry processing
    must never wait for Scenario Engine processing.
    """

    def __init__(self):

        # Structure:
        #
        # {
        #     "can.telemetry": {
        #         "scenario_engine": Subscription(...)
        #     }
        # }

        self._subscriptions: Dict[
            str,
            Dict[str, Subscription]
        ] = {}

        self._lock = RLock()

    def subscribe(
        self,
        topic: str,
        subscriber_id: str,
        maxsize: int = 1000,
        overflow_policy: str = "drop_oldest"
    ) -> Subscription:
        """
        Subscribe to a topic.

        Example:

            subscription = event_bus.subscribe(
                "can.telemetry",
                "scenario_engine"
            )
        """

        subscription = Subscription(
            topic=topic,
            subscriber_id=subscriber_id,
            maxsize=maxsize,
            overflow_policy=overflow_policy
        )

        with self._lock:

            subscribers = self._subscriptions.setdefault(
                topic,
                {}
            )

            # subscriber_id is unique per topic.
            #
            # If the connector is recreated/reloaded,
            # the new subscription replaces the old one.

            subscribers[subscriber_id] = subscription
            print(
                "### EVENTBUS SUBSCRIBE"
                " | bus_id=%s"
                " | topic=%s"
                " | subscriber=%s"
                " | count=%s ###"
                % (
                    id(self),
                    topic,
                    subscriber_id,
                    len(subscribers)
                ),
                flush=True
            )

        return subscription

    def unsubscribe(
        self,
        topic: str,
        subscriber_id: str,
        subscription=None
    ) -> None:
        with self._lock:
            subscribers = self._subscriptions.get(topic)

            if subscribers is None:
                return

            current_subscription = subscribers.get(
                subscriber_id
            )

            if current_subscription is None:
                return

            # If a specific subscription object is supplied,
            # remove it only if it is still the active one.
            #
            # This prevents an old Connector instance from
            # removing a newer subscription after remote reload.
            if (
                subscription is not None
                and current_subscription is not subscription
            ):
                return

            subscribers.pop(
                subscriber_id,
                None
            )

            if not subscribers:
                self._subscriptions.pop(
                    topic,
                    None
                )
    def publish(
        self,
        topic: str,
        payload: dict,
        source: str = "",
        correlation_id: str = None
    ) -> int:
        """
        Publish an event.

        This method is NON-BLOCKING.

        Returns:
            Number of subscriber queues that received the event.
        """

        event = BusEvent(
            topic=topic,
            payload=payload,
            source=source,
            correlation_id=correlation_id
        )

        # Copy subscribers while holding the lock.
        # Queue operations happen after releasing the lock.

        with self._lock:

            subscribers = list(
                self._subscriptions.get(
                    topic,
                    {}
                ).values()
            )
        print(
            "### EVENTBUS PUBLISH"
            " | bus_id=%s"
            " | topic=%s"
            " | subscribers=%s"
            " | source=%s ###"
            % (
                id(self),
                topic,
                len(subscribers),
                source
            ),
            flush=True
        )

        delivered = 0

        for subscription in subscribers:

            if subscription._push(event):
                delivered += 1

        return delivered

    def subscriber_count(
        self,
        topic: str
    ) -> int:
        """
        Useful for diagnostics.
        """

        with self._lock:

            return len(
                self._subscriptions.get(
                    topic,
                    {}
                )
            )


# ============================================================
# Global Event Bus Singleton
# ============================================================

def get_event_bus() -> EventBus:
    """
    Return one process-wide EventBus instance.

    The object is stored in Python's builtins namespace so it
    survives ThingsBoard extension/module reloads.
    """

    bus_name = "_smart_panel_global_event_bus"

    if not hasattr(builtins, bus_name):
        setattr(
            builtins,
            bus_name,
            EventBus()
        )

    return getattr(
        builtins,
        bus_name
    )
