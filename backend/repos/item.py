from sqlalchemy.orm import Session

from models.item import ItemModel


class ItemRepo:
    def __init__(self, db: Session):
        self.__db = db

    def create(self, item: ItemModel):
        self.__db.add(item)
        self.__db.commit()
        self.__db.refresh(item)
        return item

    def get_all(self):
        return self.__db.query(ItemModel).all()

    def get_by_id(self, item_id: int):
        return self.__db.get(ItemModel, item_id)

    def delete(self, item_id: int):
        item = self.get_by_id(item_id)
        if item:
            self.__db.delete(item)
            self.__db.commit()
        return item
