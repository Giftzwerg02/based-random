from enum import Enum
import re
from typing import Generator, Iterable, List, TypeVar
import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import concurrent.futures

_pool = concurrent.futures.ThreadPoolExecutor(max_workers=64)

_base_url = 'https://based.cooking'

def _get(path: str = "", **kwargs) -> requests.Response:
    return requests.get(f'{_base_url}/{path}', **kwargs)

def _time() -> int:
    now = datetime.now()
    return int(now.timestamp() * 10**6) 

def _iter_time() -> Generator[int, None, None]:
    while True:
        ts = _time()
        bit = 1
        while ts >= bit:
            yield 1 if ts & bit else 0
            bit = bit << 1

def _categories(soup: BeautifulSoup):
    l = soup.find(id='tagcloud')
    assert l is not None 
    assert not isinstance(l, NavigableString)
    return l.find_all('li')


_T = TypeVar('_T')
def _time_filter(iter: Iterable[_T]) -> List[_T]:
    bits = _iter_time()
    return [a for a, b in zip(iter, bits) if b == 1]

def _select_recipie(selected_cat):
    href = selected_cat.find('a')['href']
    catlist = requests.get(href)
    soup = BeautifulSoup(catlist.text, 'html.parser')
    recipies = soup.find_all('a')

    assert recipies is not None 
    assert not isinstance(recipies, NavigableString)

    return _time_filter(recipies)

def _ingridients(recipie):
    r = _get(recipie['href'])
    soup = BeautifulSoup(r.text, 'html.parser')
    ingr = soup.find(id='ingredients')
    if ingr is None:
        return []

    ingrsul = ingr.find_next_sibling('ul')
    if ingrsul is None:
        return []

    assert not isinstance(ingrsul, NavigableString)

    ingrs = ingrsul.find_all('li')
    return [i.text for i in ingrs]

class _UnitType(Enum):
    Freedome = 0
    HolySI = 1

def _parse_unit_type(s: str) -> _UnitType:
    holy_si_indicators = [ # open for more details
        r'\d+\s?g',
        r'\d+\s?ml',
        r'\d+\s?grams'
    ]

    for si_indicator in holy_si_indicators:
        if re.search(si_indicator, s):
            return _UnitType.HolySI

    return _UnitType.Freedome
