from memory.memory import Memory


class MemoryRetriever:

    def retrieve(
        self,
        memories: list[Memory],
        query: str
    ):

        query_words = set(
            query.lower().split()
        )

        if not query_words:
            return []

        results = []

        for memory in memories:

            text = (
                f"{memory.title} "
                f"{memory.content}"
            ).lower()

            score = 0

            for word in query_words:

                if len(word) < 2:
                    continue

                if word in text:
                    score += 1

            if score > 0:

                # Importance küçük bir bonus
                # olarak kullanılıyor.
                score += memory.importance * 0.25

                results.append(
                    (score, memory)
                )

        results.sort(
            key=lambda item: item[0],
            reverse=True
        )

        # LLM'e gereksiz memory göndermiyoruz.
        return [
            memory
            for _, memory in results[:5]
        ]