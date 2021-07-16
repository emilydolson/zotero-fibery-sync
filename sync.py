import pycurl
import certifi
from io import BytesIO
from urllib.parse import urlencode
import json
from inspect import getframeinfo, stack
import os
from pyzotero import zotero
import sys


get_lit_query = '[{"command": "fibery.entity/query", "args": {"query": {"q/from": "Zotero/Literature","q/select": ["Zotero/name",  "fibery/id", "Zotero/Zotero Key", "Zotero/Zotero link", "Zotero/Zotero version", {"Zotero/Authors": {"q/select": ["fibery/id", "Zotero/First name", "Zotero/Last name"], "q/limit": "q/no-limit" }}], "q/limit": "q/no-limit"}}}]'
get_authors_query = '[{"command": "fibery.entity/query", "args": {"query": {"q/from": "Zotero/Author","q/select": ["Zotero/First name", "Zotero/Last name", "fibery/id"], "q/limit": "q/no-limit"}}}]'

if os.path.exists("fibery_token.txt"):
    fb_file = open("fibery_token.txt")
    fibery_token = fb_file.readlines()[0]
    fb_file.close()
else:
    fibery_token = sys.argv[1]


def main():

    if os.path.exists("zotero_lib.txt"):
        fb_file = open("zotero_lib.txt")
        zotero_lib = fb_file.readlines()[0]
        fb_file.close()
    else:
        zotero_lib = sys.argv[2]

    zot = zotero.Zotero(zotero_lib, "group")

    lit = get_lit()
    authors = get_authors()

    for item in zot.top():
        # print(item)

        # Update literature
        if item["key"] not in lit:
            if "title" not in item["data"]:
                item["data"]["title"] = item["key"]
            result = make_api_call(f'[{{"command": "fibery.entity/create", "args": {{"type": "Zotero/Literature", "entity": {{"Zotero/name" : "{item["data"]["title"]}", "Zotero/Zotero Key": "{item["key"]}", "Zotero/Zotero link": "{item["links"]["alternate"]["href"]}", "Zotero/Zotero version": "{item["version"]}" }}}}}}]')
            item_id = result[0]["result"]["fibery/id"]

            # Add authors
            # print(f'[{{"command": "fibery.entity/add-collection-items", "args": {{"type": "Zotero/Literature", "field": "Literature/Authors", "entity": {{"fibery/id": "{item_id}"  }}, "items": {author_list_string} }}}}]')
            author_list_string = assemble_author_list(item, authors)
            make_api_call(f'[{{"command": "fibery.entity/add-collection-items", "args": {{"type": "Zotero/Literature", "field": "Zotero/Authors", "entity": {{"fibery/id": "{item_id}"  }}, "items": {author_list_string} }}}}]')
            
        else:
            fib_version = lit[item["key"]]["Zotero/Zotero version"]
            if fib_version is None:
                fib_version = 0
            if int(fib_version) < int(item["version"]):
                if "title" not in item["data"]:
                    make_api_call(f'[{{"command": "fibery.entity/update", "args": {{"type": "Zotero/Literature", "entity": {{"fibery/id": "{lit[item["key"]]["fibery/id"]}", "Zotero/Zotero Key": "{item["key"]}", "Zotero/Zotero link": "{item["links"]["alternate"]["href"]}", "Zotero/Zotero version": "{item["version"]}"  }}}}}}]')
                else:
                    make_api_call(f'[{{"command": "fibery.entity/update", "args": {{"type": "Zotero/Literature", "entity": {{"fibery/id": "{lit[item["key"]]["fibery/id"]}", "Zotero/name" : "{item["data"]["title"]}", "Zotero/Zotero Key": "{item["key"]}", "Zotero/Zotero link": "{item["links"]["alternate"]["href"]}", "Zotero/Zotero version": "{item["version"]}"  }}}}}}]')

                # Add authors
                author_list_string = assemble_author_list(item, authors)
                make_api_call(f'[{{"command": "fibery.entity/add-collection-items", "args": {{"type": "Zotero/Literature", "field": "Zotero/Authors", "entity": {{"fibery/id": "{lit[item["key"]]["fibery/id"]}"  }}, "items": {author_list_string} }}}}]')


def validate_result(result):
    # print(result)
    if result[0]["success"] != True:
        print("Error:", getframeinfo(stack()[1][0]), result)
        exit()


def make_api_call(post_data):
    # print(post_data)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, "https://ecode.fibery.io/api/commands")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    # c.setopt(c.VERBOSE, True)

    # Sets request method to POST,
    # Content-Type header to application/x-www-form-urlencoded
    # and data to send in request body.
    c.setopt(c.POSTFIELDS, post_data.encode(encoding='UTF-8', errors='replace'))
    c.setopt(pycurl.HTTPHEADER, ['Authorization: Token ' + fibery_token, 'Content-Type: application/json'])
    c.perform()
    body = buffer.getvalue()
    body = body.decode('iso-8859-1')
    data = json.loads(body)
    # s = json.dumps(data, indent=4, sort_keys=True)
    validate_result(data)
    return data


def get_lit():
    lit = make_api_call(get_lit_query)
    validate_result(lit)

    # print(lit)

    lit_dict = {}
    for item in lit[0]["result"]:
        # print(item)
        lit_dict[item["Zotero/Zotero Key"]] = item

    return lit_dict


def get_authors():
    authors = make_api_call(get_authors_query)
    validate_result(authors)

    # print(authors)

    author_dict = {}
    for item in authors[0]["result"]:
        # print(item)
        first = item["Zotero/First name"]
        last = item["Zotero/Last name"]
        if last not in author_dict:
            author_dict[last] = {}
        if first not in author_dict[last]:
            author_dict[last][first] = item

    return author_dict


def assemble_author_list(item, authors):
    item_authors = []
    for creator in item["data"]["creators"]:
        if creator["creatorType"] != "author":
            continue
        last = creator["lastName"].strip()
        first = creator["firstName"].split()[0].strip()
        
        # Strip out characters fibery can't handle. This isn't ideal
        first = ''.join(e for e in first if e.isalnum())
        last = ''.join(e for e in last if e.isalnum())

        # print(creator)
        if last not in authors or first not in authors[last]:
            # print(first, "|", last)
            result = make_api_call(f'[{{"command": "fibery.entity/create", "args": {{"type": "Zotero/Author", "entity": {{"Zotero/First name" : "{first}", "Zotero/Last name": "{last}"}}}}}}]')
            item_authors.append('{"fibery/id": "' + result[0]["result"]["fibery/id"] + '"}')
            if last not in authors:
                authors[last] = {}
            authors[last][first] = result[0]["result"]
        else:
            item_authors.append('{"fibery/id": "' + authors[last][first]["fibery/id"] + '"}')

    return "[" + ", ".join(item_authors) + "]"


if __name__ == "__main__":
    main()
