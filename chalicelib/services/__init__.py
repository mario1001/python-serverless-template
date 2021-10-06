# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice service main module.

Defines the different functions on service layer. Also
here stays the interface for services (every service should
inherit from that class to be injected).

Also contains the shared values and instances used
by service layer, along with the external interaction
ones (as the main service for controller layer).
"""


from chalicelib.services.service import Service
from chalicelib.services.main_service import MainService

main_service: MainService = MainService()
