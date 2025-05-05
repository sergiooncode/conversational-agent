import csv
import numpy as np

from django.core.management import BaseCommand, CommandParser
from sentence_transformers import SentenceTransformer, util

from agent.services.rag.sbert_net.service import RagService


class Command(BaseCommand):
    help = "Create a speech from text for a conversation"

    def add_arguments(self, parser: CommandParser) -> None:
        pass

    def _save_answer_embeddings(self):
        answers = []

        with open("../resources/rag_answers.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                answers.append(row["text"])

        model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, local

        answer_embeddings = model.encode(answers, normalize_embeddings=True)
        print(answer_embeddings)

        # Save
        np.savez("answer_embeddings.npz",
                 embeddings=answer_embeddings,
                 answers=np.array(answers, dtype=object))

        print("Saved embeddings and answers.")

    def _find_embeddings_close_to_answer(self):
        query = "Where is my refund?"

        model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, local

        answers = []

        with open("../resources/rag_answers.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                answers.append(row["text"])

        answer_embeddings = model.encode(answers, normalize_embeddings=True)

        query_embedding = model.encode(query, normalize_embeddings=True)

        scores = (
            util.cos_sim(query_embedding, answer_embeddings)[0].cpu().numpy()
        )  # Make sure it's a numpy array

        top_k = 5  # how many to retrieve
        if top_k > len(scores):
            top_k = len(scores)

        top_indices = np.argpartition(-scores, top_k - 1)[:top_k]  # Fast partial sort
        top_indices = top_indices[
            np.argsort(-scores[top_indices])
        ]  # Sort top_k scores descending

        relevant_answers = [answers[i] for i in top_indices]
        print("Relevant answers:")
        for ans in relevant_answers:
            print(ans)

    def handle(self, *args, **options) -> str | None:
        #self._save_answer_embeddings()
        service = RagService()
        print(service.get_relevant_answers("i have an issue"))
