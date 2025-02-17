from enum import Enum
import re
from typing import Generator, Iterable, List, TypeVar
import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import itertools
import concurrent.futures

pool = concurrent.futures.ThreadPoolExecutor(max_workers=64)

base_url = 'https://based.cooking'

def get(path: str = "", **kwargs) -> requests.Response:
    return requests.get(f'{base_url}/{path}', **kwargs)

def time() -> int:
    now = datetime.now()
    return int(now.timestamp() * 10**6) 

def iter_time() -> Generator[int]:
    while True:
        ts = time()
        bit = 1
        while ts >= bit:
            yield 1 if ts & bit else 0
            bit = bit << 1

def categories(soup: BeautifulSoup):
    l = soup.find(id='tagcloud')
    assert l is not None 
    assert not isinstance(l, NavigableString)
    return l.find_all('li')


T = TypeVar('T')
def time_filter(iter: Iterable[T]) -> List[T]:
    bits = iter_time()
    return [a for a, b in zip(iter, bits) if b == 1]

def select_recipie(selected_cat):
    print(f'selecting for: {selected_cat.text}')
    href = selected_cat.find('a')['href']
    catlist = requests.get(href)
    soup = BeautifulSoup(catlist.text, 'html.parser')
    recipies = soup.find_all('a')

    assert recipies is not None 
    assert not isinstance(recipies, NavigableString)

    return time_filter(recipies)

def ingridients(recipie):
    r = get(recipie['href'])
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

class UnitType(Enum):
    Freedome = 0
    HolySI = 1

def parse_unit_type(s: str) -> UnitType:
    holy_si_indicators = [ # open for more details
        r'\d+\s?g',
        r'\d+\s?ml',
        r'\d+\s?grams'
    ]

    for si_indicator in holy_si_indicators:
        if re.search(si_indicator, s):
            return UnitType.HolySI

    return UnitType.Freedome

def main():
    r = get() 
    soup = BeautifulSoup(r.text, 'html.parser')
    cats = categories(soup)
    selected_cats = time_filter(cats) 

    recipies = list(pool.map(select_recipie, selected_cats))
    flattened_recipies = list(itertools.chain.from_iterable(recipies))
    ingris = list(pool.map(ingridients, flattened_recipies))
    flattened_ingris = list(itertools.chain.from_iterable(ingris))
    parsed_units = list(map(parse_unit_type, flattened_ingris))
    
    mantissa_size = 53 # i guess
    selected_units = list(itertools.islice(parsed_units, mantissa_size))
    result = 0
    
    for idx, unit in enumerate(selected_units):
        pos = (-1) * (idx + 1)
        result += unit.value * (2 ** pos)

    print(result)
    

if __name__ == '__main__':
    main()
