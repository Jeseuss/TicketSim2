from PositionalList import PositionalList
from PriorityQueueBase import PriorityQueueBase

class UnsortedPriorityQueue(PriorityQueueBase):
    """A min-oriented priority queue implemented with an unsorted list."""

    def __init__(self):
        """Create a new empty Priority Queue."""
        self._data = PositionalList()
        self._min_position = None

    def __len__(self):
        """Return the number of items in the priority queue."""
        return len(self._data)

    def add(self, key, value):
        """Add a key-value pair."""
        new_item = self._Item(key, value)
        new_position = self._data.add_last(new_item)
        
        # Update min reference
        if self._min_position is None or new_item < self._min_position.element():
            self._min_position = new_position

    def min(self):
        """Return but do not remove (k,v) tuple with minimum key. O(1) time."""
        if self.is_empty():
            raise Exception("Priority queue is empty.")
        item = self._min_position.element()
        return (item._key, item._value)

    def remove_min(self):
        """Remove and return (k, v) tuple with minimum key."""
        if self.is_empty():
            raise Exception("Priority queue is empty.")
        
        # Remove the minimum element
        min_item = self._data.delete(self._min_position)
        
        # Find new minimum by scanning remaining elements
        self._min_position = None
        if not self.is_empty():
            self._min_position = self._data.first()
            walk = self._data.after(self._min_position)
            while walk is not None:
                if walk.element() < self._min_position.element():
                    self._min_position = walk
                walk = self._data.after(walk)
        
        return (min_item._key, min_item._value)