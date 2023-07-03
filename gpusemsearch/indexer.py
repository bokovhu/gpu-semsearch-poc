import sentence_transformers
import os
import json
import tqdm
import numpy as np
from .disassembler import Disassembler


class Indexer:
    def __init__(
        self,
        directory: str,
        index_directory="./index",
        indexed_extensions=[".txt", ".md"],
        embedding_model_id="all-MiniLM-L6-v2",
        cuda_device="cuda:0",
    ) -> None:
        self.input_directory = directory
        self.index_directory = index_directory
        self.indexed_extensions = indexed_extensions
        self.embedding_model_id = embedding_model_id
        self.cuda_device = cuda_device

    def run(self):
        files_to_index = []
        for root, dirs, files in os.walk(self.input_directory):
            for file in files:
                indexed_by_extension = False
                for extension in self.indexed_extensions:
                    if file.endswith(extension):
                        indexed_by_extension = True
                        break
                if indexed_by_extension:
                    files_to_index.append(os.path.join(root, file))
        print(f"Found {len(files_to_index)} files to index")

        # Create the output directory if it does not exists
        if not os.path.exists(self.index_directory):
            os.makedirs(self.index_directory)

        embedding_model = sentence_transformers.SentenceTransformer(
            self.embedding_model_id, device=self.cuda_device
        )

        disassembler = Disassembler(
            num_sentences=5,
            window_slide=3
        )

        for file_to_index in tqdm.tqdm(files_to_index):
            file_content = ""
            file_basename = os.path.basename(file_to_index)
            with open(file_to_index, "r", encoding="utf-8") as f:
                file_content = f.read()

            sentences = disassembler.disassemble(file_content)

            indexed_texts = []

            for sentence_tuple in sentences:
                indexed_texts += [" ".join(sentence_tuple)]

            index_batches = []
            batch_size = 64

            for i in range(0, len(indexed_texts), batch_size):
                batch = indexed_texts[i : i + batch_size]
                index_batches.append(batch)

            embeddings = []

            for batch in index_batches:
                batch_embeddings = embedding_model.encode(batch)
                embeddings += [e.tolist() for e in batch_embeddings]

            embeddings = np.array(embeddings)
            np.save(f"{self.index_directory}/{file_basename}.npy", embeddings)
            with open(
                f"{self.index_directory}/{file_basename}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(indexed_texts, f, indent=2)
            with open(
                f"{self.index_directory}/{file_basename}.sentences.json", "w", encoding="utf-8"
            ) as f:
                json.dump(sentences, f, indent=2)