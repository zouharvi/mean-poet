import langdetect

def langdetect_safe(poem_src, poem_ref, poem_hyp, log_str=[]):
    """
    Detects languages and throws adequate errors.
    """
    try:
        lang_src = langdetect.detect(poem_src)
    except:
        log_str.append("Unable to recognize src language")
        lang_src = "unk"

    try:
        lang_ref = langdetect.detect(poem_ref)
    except:
        log_str.append("Unable to recognize ref language")
        lang_ref = "unk"

    try:
        lang_hyp = langdetect.detect(poem_hyp)
    except:
        log_str.append("Unable to recognize hyp language")
        lang_hyp = "unk"

    log_str.append(
        f"Recognized languages: {lang_src} -> {lang_ref} & {lang_hyp}"
    )

    if lang_ref != lang_hyp:
        log_str.append(
            "WARNING: Reference and translate version languages do not match"
        )
    if lang_src == lang_ref:
        log_str.append(
            "WARNING: Source and reference version languages are the same (not a translation)"
        )
    if lang_src == lang_hyp:
        log_str.append(
            "WARNING: Source and translated version languages are the same (not a translation)"
        )

    return lang_src, lang_ref, lang_hyp

