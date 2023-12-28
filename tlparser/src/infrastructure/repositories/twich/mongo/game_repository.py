"""
game_repository.py: File, containing twich game mongo repository implementation.
"""


from typing import Optional
from domain.entities.twich.game_entity import TwichGameEntity
from domain.events.twich.game_events import (
    PublicParseGameCalledEvent,
    TwichGameCreatedOrUpdatedEvent,
    TwichGameDeletedByNameEvent,
)
from domain.exceptions.twich.game_exceptions import GameNotFoundException
from domain.interfaces.repositories.twich.game_repository import ITwichGameRepository
from domain.types.types import ResultWithEvent
from infrastructure.connections.mongo.database import MongoDatabase
from infrastructure.mappers.twich.mongo.game_mapper import TwichGameMapper
from infrastructure.models.twich.mongo.game_model import TwichGame


class TwichGameMongoRepository(ITwichGameRepository):
    """
    TwichGameMongoRepository: Mongo implementation of ITwichGameRepository.

    Args:
        ITwichGameRepository (_type_): Repository abstract class.
    """

    def __init__(self, db: MongoDatabase) -> None:
        """
        __init__: Initialize repository.

        Args:
            db (MongoDatabase): MongoDatabase instance, containing mongo connection.
        """

        self.db: MongoDatabase = db

    def parse_game(self, name: str) -> PublicParseGameCalledEvent:
        """
        parse_game: Return event about parsing twich game.

        Args:
            name (str): Name of the game.

        Returns:
            PublicParseUserCalledEvent: Event about parsing game.
        """

        return PublicParseGameCalledEvent(type='twich_game', name=name)

    def create_or_update(
        self, game_entity: TwichGameEntity
    ) -> ResultWithEvent[TwichGameEntity, TwichGameCreatedOrUpdatedEvent]:
        """
        create_or_update: Create or update twich game.

        Args:
            game_entity (TwichGameEntity): Twich game entity.

        Returns:
            ResultWithEvent[Result, Event]:: Created/Updated twich game entity.
        """

        game_persistence = TwichGameMapper.to_persistence(game_entity)
        game_persistence.save()

        event: TwichGameCreatedOrUpdatedEvent = TwichGameCreatedOrUpdatedEvent(
            id=game_persistence.id,
            name=game_persistence.name,
            igdb_id=game_persistence.igdb_id,
            box_art_url=game_persistence.box_art_url,
            parsed_at=game_persistence.parsed_at,
        )
        entity: TwichGameEntity = TwichGameMapper.to_domain(game_persistence)

        return ResultWithEvent[TwichGameEntity, TwichGameCreatedOrUpdatedEvent](
            result=entity,
            event=event,
        )

    def all(self) -> list[TwichGameEntity]:
        """
        all: Return list of twich games.

        Returns:
            list[TwichGameEntity]: List of twich games.
        """

        return [
            TwichGameMapper.to_domain(game_persistence) for game_persistence in TwichGame.objects
        ]

    def delete_game_by_name(self, name: str) -> TwichGameDeletedByNameEvent:
        """
        delete_game_by_name: Delete game by name.

        Args:
            name (str): Name of the game.

        Returns:
            TwichGameDeletedByNameEvent: Twich game deleted event.
        """

        for game_persistence in TwichGame.objects(name=name):
            game_persistence.delete()

        return TwichGameDeletedByNameEvent(name=name)

    def get_game_by_name(self, name: str) -> TwichGameEntity:
        """
        get_game_by_name: Return game by name.

        Args:
            name (str): Name of the game.

        Returns:
            TwichGameEntity: Twich game entity.
        """

        game_persistence: Optional[TwichGame] = TwichGame.objects(name=name).first()

        if not game_persistence:
            raise GameNotFoundException

        return TwichGameMapper.to_domain(game_persistence)
