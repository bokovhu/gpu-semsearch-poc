from gpusemsearch import Indexer

if __name__ == "__main__":
    indexer = Indexer(directory="./input.github-referenced-readmes", index_directory="./index.github-referenced-readmes")
    indexer.run()
