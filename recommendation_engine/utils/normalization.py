def normalize(value, minimum, maximum):

    if maximum == minimum:
        return 1.0

    return (
        (value - minimum)
        / (maximum - minimum)
    )