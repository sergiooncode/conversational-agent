import csv
import numpy as np

from django.core.management import BaseCommand, CommandParser
from sentence_transformers import SentenceTransformer, util


class Command(BaseCommand):
    help = "Create a speech from text for a conversation"

    def add_arguments(self, parser: CommandParser) -> None:
        pass

    def handle(self, *args, **options) -> str | None:
        answers = []

        with open("../resources/answers_for_rag.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                answers.append(row["text"])

        model = SentenceTransformer('all-MiniLM-L6-v2')  # small, fast, local

        answer_embeddings = model.encode(answers, normalize_embeddings=True)

        query = "Where is my refund?"

        query_embedding = model.encode(query, normalize_embeddings=True)

        scores = util.cos_sim(query_embedding, answer_embeddings)[0]
        top_k = 3  # how many to retrieve
        top_indices = np.argsort(scores)[-top_k:][::-1]

        relevant_answers = [answers[i] for i in top_indices]

        print("Relevant answers:")
        for ans in relevant_answers:
            print(ans)
