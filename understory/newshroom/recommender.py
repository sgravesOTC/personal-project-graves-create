import redis
from django.conf import settings
from .models import Article

r = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    db = settings.REDIS_DB
)

class ArticleRecommender:
    def get_article_key(self, id):
        return f'article:{id}:read_with'

    def articles_read(self, article_list):
        """
        Call this when an article is viewed.
        """
        article_ids = [a.id for a in article_list]
        for article_id in article_ids:
            for with_id in article_ids:
                if article_id != with_id:
                    r.zincrby(self.get_article_key(article_id), 1, with_id)

    def suggest_articles_for(self, article, max_results=4):
        """
        Returns articles frequently read alongside this one, ordered by co-occurence score.
        """
        suggestions = r.zrange(
            self.get_article_key(article.id), 0, -1, desc=True
        )[:max_results]

        suggested_ids = [int(id) for id in suggestions]
        suggested_articles = list(
            Article.publisher.filter(id__in=suggested_ids)
        )
        suggested_articles.sort(key=lambda x: suggested_ids.index(x.id))
        return suggested_articles
