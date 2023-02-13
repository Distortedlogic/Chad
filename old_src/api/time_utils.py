def maybe_separtor(use: bool):
    if use:
        return ", "
    else:
        return ''


def secondsToText(secs: int):
    days = int(secs // 86400)
    hours = int((secs - days * 86400) // 3600)
    minutes = int((secs - days * 86400 - hours * 3600) // 60)
    seconds = int(secs - days * 86400 - hours * 3600 - minutes * 60)
    use = True
    if seconds == 0:
        use = False
    return (
        (f"{days}d, " if days else "")
        + (f"{hours}h, " if hours else "")
        + (f"{minutes}m"+maybe_separtor(use) if minutes else "")
        + (f"{seconds}s" if seconds else "")
    )
