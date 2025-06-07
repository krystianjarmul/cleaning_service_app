from typing import TypeVar, Generic, Any

from django.db import connection
from django.db.models import Model, QuerySet, Prefetch

ModelType = TypeVar('ModelType', bound=Model)

class BaseRepository(Generic[ModelType]):
    _model: type[ModelType]

    def get_list(
            self,
            filter_params: dict[str, Any] | None = None,
            filter_q: dict[str, Any] | None = None,
            fields: list[str] | None = None,
            select_related: list[str] | None = None,
            prefetch_related: list[str | Prefetch] | None = None,
            order_by: list[str] | None = None,
            query: QuerySet[ModelType] | None = None,
            iterator: dict[str, Any] | None = None,

    ) -> QuerySet[ModelType] | list | dict:
        if query is not None:
            if hasattr(query, 'all') and not isinstance(query, QuerySet):
                query = query.all()
        else:
            query = self._model.objects.all()

        if filter_params:
            query = query.filter(**filter_params)

        if filter_q:
            query = query.filter(filter_q)

        if select_related:
            query = query.select_related(*select_related)

        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)

        if order_by:
            query = query.order_by(*order_by)

        if fields:
            if len(fields) == 1:
                query = query.values_list(fields[0], flat=True)
            else:
                query = query.values(*fields)

        if iterator:
            query = query.iterator(**iterator)

        return query

    def bulk_create(self, items: list[ModelType]) -> list[ModelType]:
        return self._model.objects.bulk_create(items)

    def drop_all(self):
        self._model.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute(f"ALTER SEQUENCE public.{self._model._meta.db_table}_id_seq RESTART WITH 1;")
