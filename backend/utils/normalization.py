def normalize(value, minimum=0, maximum=1):

    if maximum == minimum:
        return 0

    return (value - minimum) / (
        maximum - minimum
    )
