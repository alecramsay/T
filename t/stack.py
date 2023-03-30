# stack.py
#!/usr/bin/env python3

"""
STACK
"""

from collections import deque
from typing import Any


class Stack:
    _queue_: deque[Any]

    def __init__(self) -> None:
        self._queue_ = deque([])

    def push(self, item) -> None:
        self._queue_.appendleft(item)

    def pop(self) -> Any:
        return self._queue_.popleft()

    def isempty(self) -> bool:
        return not self._queue_

    def len(self) -> int:
        return len(self._queue_)

    def clear(self) -> None:
        self._queue_.clear()

    # aka 'peek' or top'
    def first(self) -> Any:
        return self._queue_[0]

    def second(self) -> Any:
        return self._queue_[1]

    def replace_top(self, item) -> None:
        self._queue_[0] = item

    def swap(self) -> None:
        first: Any = self.pop()
        second: Any = self.pop()
        self.push(first)
        self.push(second)

    # Other easy possible ops, given 'deque' capabilities

    def reverse(self) -> None:
        self._queue_.reverse()

    def rotate(self) -> None:
        self._queue_.rotate()


"""
OTHER HP CALC STACK OPERATIONS:

(defun stack-roll-down! (s)
  (let ((l (stack-items s)))
    (set-stack-items! s (add-last (cdr l) (car l)))
    ))

(defun stack-roll-up! (s)
  (let ((l (stack-items s)))
    (set-stack-items! s (cons (last l) (remove-last l)))
    ))
"""

### END ###
