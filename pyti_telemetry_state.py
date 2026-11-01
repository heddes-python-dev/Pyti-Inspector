"""Convert Pyti state and script locals into bounded JSON-safe snapshots."""


DIRECTIONS = ("north", "east", "south", "west")


def json_value(value, depth=0):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value if not isinstance(value, str) or len(value) <= 500 else value[:497] + "..."
    if depth >= 3:
        return f"<{type(value).__name__}>"
    if isinstance(value, (list, tuple, set)):
        return [json_value(item, depth + 1) for item in list(value)[:100]]
    if isinstance(value, dict):
        return {
            str(key)[:100]: json_value(item, depth + 1)
            for key, item in list(value.items())[:100]
            if isinstance(key, (str, int, float, bool))
        }
    return f"<{type(value).__name__}>"


def script_frame(frame):
    while frame is not None:
        if frame.f_code.co_filename == "<pyti-script>":
            return frame
        frame = frame.f_back
    return None


def variables(frame):
    if frame is None:
        return {}
    return {
        name: json_value(value)
        for name, value in list(frame.f_locals.items())[:100]
        if not name.startswith("__") and not callable(value)
    }


def state(interpreter):
    robot = interpreter.roboter
    field = interpreter.spielfeld_manager
    return {
        "x": robot.x,
        "y": robot.y,
        "direction": DIRECTIONS[robot.richtung],
        "beepers_in_bag": robot.beeper_im_inventar,
        "walls": [list(point) for point in sorted(field.wand_koordinaten)[:100]],
        "beepers": [list(point) for point in sorted(field.beeper_koordinaten)[:100]],
        "goal": list(field.ziel_position) if field.ziel_position else None,
    }
