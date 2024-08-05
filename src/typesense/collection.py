from __future__ import annotations

from typesense.api_call import ApiCall
from typesense.types.collection import CollectionSchema, CollectionUpdateSchema

from .documents import Documents
from .overrides import Overrides
from .synonyms import Synonyms
from .documents import Documents



class Collection(object):
    def __init__(self, api_call: ApiCall, name: str):
        self.name = name
        self.api_call = api_call
        self.documents = Documents(api_call, name)
        self.overrides = Overrides(api_call, name)
        self.synonyms = Synonyms(api_call, name)

    @property
    def _endpoint_path(self) -> str:
        from typesense.collections import Collections

        return f"{Collections.RESOURCE_PATH}/{self.name}"

    def retrieve(self) -> CollectionSchema:
        response: CollectionSchema = self.api_call.get(
            endpoint=self._endpoint_path, entity_type=CollectionSchema, as_json=True
        )
        return response

    def update(self, schema_change: CollectionUpdateSchema) -> CollectionUpdateSchema:
        response: CollectionUpdateSchema = self.api_call.patch(
            endpoint=self._endpoint_path,
            body=schema_change,
            entity_type=CollectionUpdateSchema,
        )
        return response

    # There's currently no parameters passed to Collection deletions, but ensuring future compatibility
    def delete(self, params: dict[str, str | bool] | None = None) -> CollectionSchema:
        return self.api_call.delete(
            self._endpoint_path, entity_type=CollectionSchema, params=params
        )
