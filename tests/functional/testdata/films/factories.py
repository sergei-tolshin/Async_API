import random

import factory
from faker import Factory as FakerFactory
from functional.testdata.films import models

fake = FakerFactory.create()
film_ids_list = [fake.uuid4() for i in range(random.randint(1, 10))]


class FilmFactory(factory.Factory):
    class Meta:
        model = models.FilmModel

    id = factory.Faker('uuid4')
    title = factory.Faker('sentence', nb_words=5)
    imdb_rating = factory.LazyAttribute(
        lambda x: round(random.uniform(0, 10), 1))
