from __APP__.__FEATURE__.application.create___entity__ import Create__Entity__
from __APP__.__FEATURE__.application.list___FEATURE__ import List__Feature__

from .fakes import InMemory__Entity__Repository


def test_list_returns_in_insertion_order() -> None:
    repo = InMemory__Entity__Repository()
    create = Create__Entity__(repo)
    first, second = create("a"), create("b")
    assert List__Feature__(repo)() == [first, second]
