import torch
import sentence_transformers
import os
import random
import json
import tqdm
import numpy as np
import threading
import struct
import datetime
import hashlib
from .disassembler import Disassembler


class SearchEngine:
    def __init__(
        self,
        index_directory: str = "./index",
        embedding_model_id="all-MiniLM-L6-v2",
        cuda_device="cuda:0",
    ) -> None:
        self.index_directory = index_directory
        self.embedding_model_id = embedding_model_id
        self.cuda_device = cuda_device
        self.indices = {}

    def load(self):
        self.embedding_model = sentence_transformers.SentenceTransformer(
            self.embedding_model_id, device=self.cuda_device
        )
        files_to_load = []
        for root, dirs, files in os.walk(self.index_directory):
            for file in files:
                if file.endswith(".npy"):
                    files_to_load.append(os.path.join(root, file))
        print(f"Found {len(files_to_load)} files to index")

        for file_to_load in tqdm.tqdm(files_to_load):
            index_data = np.load(file_to_load)
            index_texts_json_file = file_to_load.replace(".npy", ".json")
            with open(index_texts_json_file, "r", encoding="utf-8") as f:
                index_texts = json.load(f)

            index_data_tensor = torch.from_numpy(index_data).to(
                self.cuda_device, dtype=torch.float32
            )

            self.indices[file_to_load] = {
                "index_data": index_data_tensor,
                "index_texts": index_texts,
            }

    def run_query(self, search_terms: list, min_similarity: float = 0.8):
        search_term_embeddings = self.embedding_model.encode(search_terms)
        search_term_embeddings_tensor = torch.from_numpy(
            np.array(search_term_embeddings)
        ).to(self.cuda_device, dtype=torch.float32)

        search_term_embeddings_transposed = search_term_embeddings_tensor.transpose(
            0, 1
        )

        results = []

        for index_name, index_dict in self.indices.items():
            if index_dict["index_data"].shape[0] == 0:
                continue
            similarity_matrix = torch.matmul(
                index_dict["index_data"], search_term_embeddings_transposed
            )

            # Find maximum similarity for each row
            max_similarity, max_similarity_indices = torch.max(similarity_matrix, dim=1)

            matching = torch.where(max_similarity >= min_similarity)

            for match_index in matching[0]:
                result = {
                    "index": index_name,
                    "text": index_dict["index_texts"][match_index],
                    "similarity": max_similarity[match_index].item(),
                }
                results.append(result)

        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results
