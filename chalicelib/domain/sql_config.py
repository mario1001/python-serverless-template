from enum import Enum, unique


@unique
class TableNames(Enum):
    """
    Enum containing all tables defined in the database model
    """

    TABLE_NAME = "table_name"


@unique
class ModelClassNames(Enum):
    """
    Enum containing all tables defined in the database model
    """

    ENTITY_NAME = "Entity"


@unique
class ForeignKeysEnum(Enum):
    """
    Enum containing all foreign keys defined in the database model
    """

    TABLE_ID = f"{TableNames.TABLE_NAME.value}.id"


class Relationships(Enum):
    """
    Enum containing all relationships related to foreign keys
    """

    RELATIONSHIP_ENTITY = "relationship"
