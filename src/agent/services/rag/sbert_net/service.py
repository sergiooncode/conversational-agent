import csv

import numpy as np

from sentence_transformers import SentenceTransformer, util

ANSWERS_TO_RETRIEVE_MAX_NUMBER = 5


class RagService:
    def __init__(self):
        import os

        print(os.getcwd())
        data = np.load("../resources/answer_embeddings.npz", allow_pickle=True)
        self._answer_embeddings = data["embeddings"]
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        self._raw_answers = []
        with open("../resources/rag_answers.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._raw_answers.append(row["text"])

    def get_relevant_answers(self, user_message: str):
        query_embedding = self._model.encode(user_message, normalize_embeddings=True)
        scores = util.cos_sim(query_embedding, self._answer_embeddings)[0].cpu().numpy()
        top_k = ANSWERS_TO_RETRIEVE_MAX_NUMBER
        if top_k > len(scores):
            top_k = len(scores)

        top_indices = np.argpartition(-scores, top_k - 1)[:top_k]  # Fast partial sort
        top_indices = top_indices[np.argsort(-scores[top_indices])]

        relevant_answers = [self._raw_answers[i] for i in top_indices]

        context_text = "\n".join(
            [f"Relevant answer: {ans}" for ans in relevant_answers]
        )

        return f"{context_text}\n\nUser: {user_message}"
