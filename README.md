# zotero-fibery-sync

## THIS LIBRARY IS DEPRECATED! Please use the [new and improved version](https://github.com/emilydolson/zotero-fibery-sync-api) which takes advantage of Fibery's new integrations API to act as a proper integration

[![CI](https://github.com/emilydolson/zotero-fibery-sync/actions/workflows/python-app.yml/badge.svg)](https://github.com/emilydolson/zotero-fibery-sync/actions/workflows/python-app.yml)

This tool is designed to be used with [this Fibery template](https://shared.fibery.io/t/d4ab4d3a-bfe6-4574-9fdc-7a8afdef43a5-zotero). It pulls data from a zotero library (ID specified as second command-line argument or by putting it in the file zotero_lib.txt) and places it in Fibery (provide your API key as the first command-line argument or by putting it in the file fibery_token.txt).

Currently, this tool is very bare-bones and minimally tested. It only synchronizes paper names, authors, and Zotero URLs. The intention is to allow you to refer to papers elsewhere in your workspace and keep track of those references. In the future, I hope to add two-way sync of notes about papers. I welcome other feature requests too, although I can't prioritize development on this tool particularly highly (pull requests welcome!).

Usage:
```
python sync.py [FIBERY_TOKEN] [Zotero library ID]
```

Currently only supports public Zotero libraries, but it would be easy to add support for private ones.
