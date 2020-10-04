from queue import Queue
import threading
import os
from urllib.request import urlopen, Request, HTTPError, URLError, quote

threads = 1

target_url = "http://www.blackhatpython.com"
wordlist_file = "./all.txt"
resume = None
user_agent = "Mozilla/5.0 *X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"

def build_wordlist(wordlist_file):

    with open(wordlist_file, "rt") as fd:
        raw_words = fd.readlines()

    found_resume = False
    words = Queue()

    for word in raw_words:
        word = word.rstrip()

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from %s" % resume)
        else:
            words.put(word)

    return words

def dir_bruter(word_queue, extensions=None):

    while not word_queue.empty():
        attempt = word_queue.get()

        attempt_list = []

        # check if it ends with an extension ".xxx"
        # if not, it is a directory
        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)

        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        for brute in attempt_list:

            url = "%s%s" % (target_url, quote(brute))

            try:
                headers = {}
                headers["User-Agent"] = user_agent
                req = Request(url, headers=headers)
                response = urlopen(req)

                if len(response.read()):
                    print("[%d] => %s" % (response.code, url))
            
            except HTTPError as err:
                if hasattr(err, 'code') and err.code != 404:
                    print("!!! %d => %s" % (err.code, url))
                pass


word_queue = build_wordlist(wordlist_file)
extensions = [".php", ".bak", ".orig", ".inc"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extensions,))
    t.start()