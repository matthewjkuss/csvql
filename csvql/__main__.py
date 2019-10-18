"""Run."""

import logging

from csvql import web

logging.root.setLevel("DEBUG")

web.main()
