import logging
from collections.abc import Callable
from enum import Enum, auto

logger = logging.getLogger(__name__)


class EventType(Enum):
    SCRAPE_REQUESTED = auto()
    SEARCHES_REQUESTED = auto()
    SCORED_CARS_REQUESTED = auto()
    GROUPED_CARS_REQUESTED = auto()
    SCORED_CARS_AND_REGRESSION_LINE_REQUESTED = auto()


class EventBus:
    def __init__(self) -> None:
        self.subscribers: dict[EventType, list[Callable]] = {event: [] for event in EventType}

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        logger.info("Subscribing to event: %s with callback: %s", event_type, callback)
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)

    def publish(self, event_type: EventType) -> None:
        logger.info("Publishing event: %s", event_type)
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback()
