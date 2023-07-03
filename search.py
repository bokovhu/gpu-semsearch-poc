import datetime

import_start = datetime.datetime.now()
from gpusemsearch import SearchEngine

import_end = datetime.datetime.now()
print(f"Imported in {import_end - import_start}")


if __name__ == "__main__":
    load_start = datetime.datetime.now()
    search_engine = SearchEngine(index_directory="./index.github-referenced-readmes")
    search_engine.load()
    load_end = datetime.datetime.now()

    print(f"Loaded index in {load_end - load_start}")

    radius = 0.5

    while True:
        search_terms = input(f"Search terms (r={radius})> ")
        if search_terms == "exit":
            break
        if search_terms.startswith("/radius ") or search_terms.startswith("/r "):
            radius = float(search_terms.split(" ")[1])
            continue

        query_start = datetime.datetime.now()
        query_results = search_engine.run_query([search_terms], min_similarity=radius)
        query_end = datetime.datetime.now()

        print(f"Query completed in {query_end - query_start}")

        result_index = 1
        for query_result in query_results[:10]:
            print(f"Result {result_index}")
            print(f'{query_result["index"]} - {query_result["text"]}')
            print(f"Similarity: {query_result['similarity']}")
            print("--------------------")
            result_index += 1

        print("--------------------")
