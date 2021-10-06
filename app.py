# Created in June 12, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless Template lambda handler module.

Contains the lambda functions (expressing with
AWS chalice routers) along the module.
"""

from chalice import Chalice

app = Chalice(app_name="template")
app.debug = True

import chalicelib
