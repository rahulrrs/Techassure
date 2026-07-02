from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session


ModelT = TypeVar("ModelT")


class Repository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def get(self, id_: int) -> ModelT | None:
        return self.db.get(self.model, id_)

    def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        return list(self.db.scalars(select(self.model).offset(offset).limit(limit)))

    def add(self, item: ModelT) -> ModelT:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
