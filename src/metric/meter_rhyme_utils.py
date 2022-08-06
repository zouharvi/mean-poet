def meter_regularity(meter):
    """
    Output is bounded [0, 1]
    """
    score = 0
    max_score = 0
    # look at patterns, make sure to not penalize across stanza boundaries
    # TODO: replace with smarter Poesy
    last_meter = " "
    for i in range(0, len(meter)):
        if meter[i] == " ":
            last_meter = " "
            continue
        if last_meter != " ":
            max_score += 2
            if last_meter == meter[i]:
                score += 2
            elif abs(last_meter - meter[i]) < 1:
                score += 1
        last_meter = meter[i]
    return score / max(max_score, 1)


def meter_regularity_sim(reg_1, reg_2):
    """
    Output is bounded [0, 1]
    """
    # TODO: not the best function
    return 1 - abs(reg_1 - reg_2)


def line_count_sim(count_1, count_2):
    """
    Output is bounded [0, 1]
    """
    # TODO: not the best function
    return min(count_1, count_2) / max(count_1, count_2)


def rhyme_intensity(rhyme):
    if all([x == "?" for x in rhyme]):
        return 0

    # TODO: currently penalizing diverse rhymes
    return 1 / len(set(rhyme))


def rhyme_intensity_sim(acc_xxx, acc_hyp):
    """
    Output is bounded [0, 1]
    """
    acc_xxx = max(0, acc_xxx)
    acc_hyp = max(0, acc_hyp)
    # TODO: not the best function
    return min(1, 1 - (acc_xxx - acc_hyp))


def get_meter(parsed):
    meter = []
    prev_stanza = None

    fallback_syllabes = any(
        [line.bestParses()[0] is None for line in parsed.prosodic.values()])

    linelenghts_iterator = parsed.linelengths if fallback_syllabes else parsed.linelengths_bybeat

    for (_line_i, stanza_i), val in linelenghts_iterator.items():
        if prev_stanza is not None and prev_stanza != stanza_i:
            # insert stanza separator to meter
            meter.append(" ")
        meter.append(val)
        prev_stanza = stanza_i

    # print("Fallback", fallback_syllabes, meter)
    return meter


def get_rhyme(parsed):
    rhyme = []
    prev_stanza = None
    for (_line_i, stanza_i), val in parsed.rhymes.items():
        if prev_stanza is not None and prev_stanza != stanza_i:
            # insert stanza separator to rhyme
            rhyme.append(" ")
        rhyme.append(val)
        prev_stanza = stanza_i
    return "".join(rhyme).replace("-", "?").upper()


def get_rhyme_acc_safe(parsed, log_str=[]):
    try:
        return parsed.rhymed["rhyme_scheme_accuracy"]
    except:
        print(parsed)
        log_str.append("Unable to detect rhyme accuracy of TODO. Replacing with 0.")
        return 0