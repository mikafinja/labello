#!/usr/bin/env python3

"""
A web-based service designed to print labels on your Brother QL label printer.
"""

from labello import app, logger


if __name__ == '__main__':
    logger.info("starting labello webserver")
    app.run(port=app.config['port'], host=app.config['host'], threaded=True)
