from typing import List


class HasIds:
    def __init__(self, ids: List[int]):
        self.ids = ids


class Ids(HasIds):
    def is_ids_intersect(self, ids: HasIds) -> bool:
        if len(self.ids) == 0 or len(ids.ids) == 0: return True
        return len(set(self.ids) & set(ids.ids)) != 0

    def is_intersect_with_simple_postings(self) -> bool:
        return len(self.ids) == 0
