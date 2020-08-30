#!/usr/bin/env python
# coding: utf-8

# ### Author: `Abhijit Gupta`  
# ### Email: `abhijit038@gmail.com`  
# ### Feedback Form: https://forms.gle/1PkYCNZW7btYRGCAA   
# ### GIT: https://github.com/abhijitmjj/TwitterMiner  
# 

# In[9]:


import glob
import json
import os
from functools import partial
from pathlib import Path
from pprint import pprint

import pandas as pd
import regex
import requests


# In[10]:


# Descriptor for a type-checked attribute
class Typed:
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("Expected " + str(self.expected_type))
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


def typeassert(**kwargs):
    def decorate(cls):
        for name, expected_type in kwargs.items():
            # Attach a Typed descriptor to the class
            setattr(cls, name, Typed(name, expected_type))  # obj, name, value
        return cls

    return decorate


# ## IMPORTANT: `Specify the arguments for "n" and "sleep" before you proceed`

# In[11]:


def twentyFourSeven(fun, n=2, sleep=3):
    """
    n: is in hours * days (If you want to get data for a month enter 24*30)
    sleep: time to wait before firing again(in seconds)
           to wait for 1h enter 3600
    sample arguments n=24*30, sleep=3600
    """
    import time
    import os
    from pathlib import Path

    try:
        os.mkdir(dir_ := os.path.expanduser("~/TwitterMiner"))
    except FileExistsError:
        pass

    def decorate():
        arr = []
        for _ in range(n):
            result = fun()
            arr.append(result)
            with open(Path(dir_) / "data.txt", encoding="utf-8", mode="a") as f:
                pprint(result, f)
            time.sleep(sleep)
        return list(dedupe([x for y in arr for x in y], key=lambda x: x.id))

    return decorate


# In[12]:


class Structure:
    # Class Variable that specifies expected fields
    _fields = []

    def __init__(self, *args, **kwargs):
        if len(args) != len(self._fields):
            raise TypeError(f"Expected {len(self._fields)} arguments")

        # Set the arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

        # Set the additional arguments (if any)
        extra_args = kwargs.keys() - self._fields
        for name in extra_args:
            setattr(self, name, kwargs.pop(name))
        if kwargs:
            raise TypeError("Duplicate values for {}".format(",".join(kwargs)))


# In[13]:


def getUsers():
    arr = []
    while elem := input("Enter user: "):

        arr.append(elem.strip())
    return arr


auth = lambda: input("Enter your Bearer key(without quotes): ")


USERS = getUsers()

TOKEN = auth()


def create_url():
    queries = map(lambda user: f"from:{user} -is:retweet", USERS)
    tweet_fields = "tweet.fields=author_id,text,created_at"
    for elem in queries:
        url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
            elem, tweet_fields
        )
        yield url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def out_json():
    bearer_token = TOKEN
    for url in create_url():
        headers = create_headers(bearer_token)
        json_response = connect_to_endpoint(url, headers)
        resp = json.dumps(json_response, indent=4, sort_keys=True)
        yield json_response


def dedupe(items, key=None):
    seen = set()
    for item in items:
        val = item if key is None else key(item)
        if val not in seen:
            yield item
            seen.add(val)


# In[14]:


@typeassert(text=str)
class Tweet(Structure):
    _fields = []

    def __repr__(self):
        return f"Tweet(id={self.id}, author_id={self.author_id}, created_at={self.created_at}, text={self.text})"


# In[15]:


@twentyFourSeven
def data_write():

    df_ = []
    for json_ in out_json():
        df_.append(json_["data"])
    return [Tweet(**x) for y in df_ for x in y]


_ = data_write()
data = pd.DataFrame.from_dict([x.__dict__ for x in _])
data.to_excel(Path(os.path.expanduser("~/TwitterMiner")) / "TwitterMiner.xls")


# In[ ]:




