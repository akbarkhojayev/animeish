from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from main.models import Movie

class Command(BaseCommand):
    help = "Barcha filmlarning rating_avg ni 1 xonali songa yaxlitlash"

    def handle(self, *args, **options):
        movies = Movie.objects.all()

        for movie in movies:
            if movie.ratings.exists():
                agg = movie.ratings.aggregate(
                    avg_score=Avg('score'),
                    count=Count('id')
                )
                old_avg = movie.rating_avg
                new_avg = round(agg['avg_score'] or 0, 1)

                if old_avg != new_avg:
                    movie.rating_avg = new_avg
                    movie.rating_count = agg['count'] or 0
                    movie.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'"{movie.title}": {old_avg} → {new_avg}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS('Barcha ratinglar yangilandi!')
        )
