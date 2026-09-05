from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class InternetSearchService:
    """Заглушка интернет-поиска.

    Для реального поиска нужно подключить API поисковой системы
    и возвращать структурированные результаты.
    """

    def search(self, query: str, results_count: int = 5) -> list[SearchResult]:
        if not query or len(query.strip()) < 3:
            raise ValueError("Запрос слишком короткий.")

        return [
            SearchResult(
                title=f"Результат по запросу: {query}",
                url="https://example.com",
                snippet="Здесь будет краткое описание найденного материала.",
            )
        ][:results_count]
