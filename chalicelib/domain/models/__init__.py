# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice domain module.

Contains the domain model concepts (called as Python entities), attempts
to the definition of the model (class-diagram related), model is setup
with MySQL Server mainly (Amazon Aurora).

Repository layer would use these domain entities, model should be only
managed by this layer in terms of updates/reads. Also used for service DTO
creations as responses to the HTTP requests.
"""

# Database ORM Models
from chalicelib.domain.models.base import (
    Audit,
    MySQL,
)
