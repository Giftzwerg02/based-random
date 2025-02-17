import itertools
from .internal import _get, _categories, _time_filter, _select_recipie, BeautifulSoup, _pool, _ingridients, _parse_unit_type


def random() -> float:
    r = _get() 
    soup = BeautifulSoup(r.text, 'html.parser')
    cats = _categories(soup)
    selected_cats = _time_filter(cats) 

    recipies = list(_pool.map(_select_recipie, selected_cats))
    flattened_recipies = list(itertools.chain.from_iterable(recipies))
    ingris = list(_pool.map(_ingridients, flattened_recipies))
    flattened_ingris = list(itertools.chain.from_iterable(ingris))
    parsed_units = list(map(_parse_unit_type, flattened_ingris))
    
    mantissa_size = 53 # i guess
    selected_units = list(itertools.islice(parsed_units, mantissa_size))
    result = 0
    
    for idx, unit in enumerate(selected_units):
        pos = (-1) * (idx + 1)
        result += unit.value * (2 ** pos)

    return result
