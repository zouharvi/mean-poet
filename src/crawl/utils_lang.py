#!/usr/bin/env python3

import langdetect

def safe_langdetect(poem):
    try:
        return langdetect.detect(poem)
    except langdetect.lang_detect_exception.LangDetectException as e:
        return "??"
