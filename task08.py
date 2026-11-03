# Lab 4B - Task 8: The Java habit that broke the search
#
# Answers:
# 8.1 The class keeps only ONE search under the name: the second def
#     overwrites the first one completely. So ps.search("iphone") calls
#     search(query, filters) without filters -> TypeError: missing argument.
#     Python has no method overloading.
# 8.2 One search(query, *, filters=None). filters=None is used instead of
#     filters={} because a mutable default is shared between calls (the bug
#     from Lab 4A, Task 1) - the empty dict would be created once and reused.
# 8.3 I chose a keyword-only dictionary: search('iphone', filters={'brand':
#     'Apple'}). It is explicit, data-driven (keys come from the caller, not
#     hardcoded parameter names), easy to extend with new filter keys, and
#     matches the dict-shaped product records. Keyword arguments
#     (brand='Apple') look nice but do not scale: every new filterable field
#     would need a new named parameter.
# 8.4 pyflakes reports: "redefinition of unused 'search' from line 4" -
#     it finds the shadowed first definition before the code review does.
import inspect


class ProductSearch:
    def __init__(self, products):
        self.products = products

    def search(self, query: str, *, filters: dict | None = None) -> list[dict]:
        q = query.lower()
        result = [p for p in self.products if q in p["title"].lower()]
        if filters:
            for key, value in filters.items():
                result = [p for p in result if p.get(key) == value]
        return result


PRODUCTS = [
    {"title": "iPhone 15", "brand": "Apple"},
    {"title": "iPhone 15 Pro", "brand": "Apple"},
    {"title": "Galaxy S24", "brand": "Samsung"},
]


def test_search_without_filters():
    ps = ProductSearch(PRODUCTS)
    titles = [p["title"] for p in ps.search("iphone")]
    assert titles == ["iPhone 15", "iPhone 15 Pro"]


def test_search_with_filters():
    ps = ProductSearch(PRODUCTS)
    result = ps.search("iphone", filters={"brand": "Apple"})
    assert len(result) == 2
    assert ps.search("iphone", filters={"brand": "Samsung"}) == []


def test_filters_default_is_not_a_shared_dict():
    default = inspect.signature(ProductSearch.search).parameters["filters"].default
    assert default is None
