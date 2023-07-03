# GPU-based naive semantic search proof-of-concept

This repository contains a simple example for _running semantic text search on the **GPU**_. This method is really fast due to massive parallelization. The POC does the following:

* Step 0: Scrape a few awesome lists, and referenced readmes to create a dataset to search. (`scrape_github_readmes.py`)
* Step 1: Build semantic search index by embedding all documents in the dataset. (`index.py`)
* Step 2: Load the built index into VRAM and search for text queries. (`search.py`)
