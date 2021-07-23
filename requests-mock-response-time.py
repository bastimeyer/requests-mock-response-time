#!/usr/bin/env python

import argparse
import concurrent.futures
import os
import sys
from time import time

from requests import Session, __version__ as requests_version
from requests_mock import Adapter


parser = argparse.ArgumentParser()
parser.add_argument("count", nargs="?", type=int, default=1000)
parser.add_argument("threads", nargs="?", type=int, default=os.cpu_count())
args = parser.parse_args(sys.argv[1:])


session = Session()
adapter = Adapter()
session.mount("mock://", adapter)


def get(url, expected):
    now = time()
    text = session.get(url).text
    diff = time() - now
    assert text == expected

    return diff


def test(count, threads=10):
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for num in range(count):
            url = f"mock://test/{num}"
            text = str(num)
            adapter.register_uri("GET", url, text=text)
            futures.append(executor.submit(get, url=url, expected=text))

    sum = 0
    for future in concurrent.futures.as_completed(futures):
        sum += future.result()

    return sum


print(f"requests: {requests_version}")
print(f"count: {args.count}, threads: {args.threads}")
print(f"sum: {test(args.count, args.threads)}")
