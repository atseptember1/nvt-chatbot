#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MICROSOFT_APP_ID")
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD")
