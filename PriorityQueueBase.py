class PriorityQueueBase:
	"""A PriorityQueueBase class with a nested _Item class that composes a key and a value into a single object."""
	# Abstract base class for priority queue.
	class _Item:  # Lightweight composite to store priority queue items.
		__slots__ = "_key", "_value"

		def __init__(self, k, v):
			self._key = k
			self._value = v

		def __lt__(self, other):
			return self._key < other._key  # Compares items based on their keys.

		def is_empty(self):  # Return True if the queue is empty
			return len(self) == 0

