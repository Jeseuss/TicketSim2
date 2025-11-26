from _DoublyLinkedBase import _DoublyLinkedBase

class PositionalList(_DoublyLinkedBase):
    """A sequential container of elements allowing positional access."""

    # -------------------------- nested Position class -------------------------
    class Position:
        """An abstraction representing the location of a single element."""

        def __init__(self, container, node):
            """Constructor should not be invoked by user."""
            self._container = container  # Change to _container
            self._node = node           # Change to _node

        def element(self):
            """Return the element stored at this Position."""
            return self._node._element  # Use _node and _element

        def __eq__(self, other):
            """Return True if other is a Position representing the same location."""
            return type(other) is type(self) and other._node is self._node

        def __ne__(self, other):
            """Return True if other does not represent the same location."""
            return not (self == other)

    # ------------------------------- utility method ------------------------------
    def _validate(self, p):
        """Return position's node, or raise appropriate error if invalid."""
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper Position type')
        if p._container is not self:  # Use _container
            raise ValueError('p does not belong to this container')
        if p._node._next is None:  # Use _node and _next
            raise ValueError('p is no longer valid')
        return p._node

    # ------------------------------- utility method ------------------------------
    def _make_position(self, node):
        """Return Position instance for given node (or None if sentinel)."""
        if node is self._header or node is self._trailer:  # Use _header and _trailer
            return None
        else:
            return self.Position(self, node)

    # ------------------------------- accessors ------------------------------
    def first(self):
        """Return the first Position in the list (or None if list is empty)."""
        return self._make_position(self._header._next)  # Use _make_position and _header._next

    def last(self):
        """Return the last Position in the list (or None if list is empty)."""
        return self._make_position(self._trailer._prev)  # Use _make_position and _trailer._prev

    def before(self, p):
        """Return the Position just before Position p (or None if p is first)."""
        node = self._validate(p)  # Use _validate
        return self._make_position(node._prev)  # Use _make_position and _prev

    def after(self, p):
        """Return the Position just after Position p (or None if p is last)."""
        node = self._validate(p)  # Use _validate
        return self._make_position(node._next)  # Use _make_position and _next

    def __iter__(self):
        """Generate a forward iteration of the elements of the list."""
        cursor = self.first()
        while cursor is not None:
            yield cursor.element()
            cursor = self.after(cursor)

    # ------------------------------- mutators ------------------------------
    # override inherited version to return Position rather than Node
    def _insert_between(self, e, predecessor, successor):
        """Add element between existing nodes and return new Position."""
        node = super()._insert_between(e, predecessor, successor)  # Use _insert_between
        return self._make_position(node)  # Use _make_position

    def add_first(self, e):
        """Insert element e at the front of the list and return new Position."""
        return self._insert_between(e, self._header, self._header._next)  # Use _insert_between and _header

    def add_last(self, e):
        """Insert element e at the back of the list and return new Position."""
        return self._insert_between(e, self._trailer._prev, self._trailer)  # Use _insert_between and _trailer

    def add_before(self, p, e):
        """Insert element e into list before Position p and return new Position."""
        original = self._validate(p)  # Use _validate
        return self._insert_between(e, original._prev, original)  # Use _insert_between and _prev

    def add_after(self, p, e):
        """Insert element e into list after Position p and return new Position."""
        original = self._validate(p)  # Use _validate
        return self._insert_between(e, original, original._next)  # Use _insert_between and _next

    def delete(self, p):
        """Remove and return the element at Position p."""
        original = self._validate(p)  # Use _validate
        return self._delete_node(original)  # Use _delete_node

    def replace(self, p, e):
        """Replace the element at Position p with e and return the old element."""
        original = self._validate(p)  # Use _validate
        old_value = original._element  # Use _element
        original._element = e  # Use _element
        return old_value