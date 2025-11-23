from PIL import Image, ImageDraw
from Vector2 import Vector2

TAB_COLOR = (200, 200, 200)  # Light gray
FRET_COUNT = 20
STRING_COUNT = 6

"""
def render_tab(c1: Vector2, c2: Vector2, c3: Vector2, c4: Vector2, notes):
    width = abs(max(c2.x, c4.x) - min(c1.x, c3.x))
    height = abs(max(c1.y, c2.y) - min(c3.y, c4.y))

    angle1 = math.degrees(math.atan2(c3.y - c1.y, c3.x - c1.x)) # Gets angle of left side
    angle2 = math.degrees(math.atan2(c4.y - c2.y, c4.x - c2.x)) # Gets angle of right side

    angle = abs(angle1 - angle2)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.line((c1.x, c1.y, c2.x, c2.y), fill=TAB_COLOR, width=2)
    draw.line((c1.x, c1.y, c3.x, c3.y), fill=TAB_COLOR, width=2)
    draw.line((c3.x, c3.y, c4.x, c4.y), fill=TAB_COLOR, width=2)
    draw.line((c2.x, c2.y, c4.x, c4.y), fill=TAB_COLOR, width=2)

    for i in range(FRET_COUNT + 1):
        for j in range(6):
            # string index is 1-based (1..6), fret number is i (0..FRET_COUNT)
            coord = note_to_position(Vector2(j + 1, i), c1, c2, c3, c4)
            x = int(coord.x)
            y = int(coord.y)
            # draw a small dot for this string/fret intersection
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=TAB_COLOR)
    
    for note in notes:
        coord = note_to_position(note, c1, c2, c3, c4)
        x = int(coord.x)
        y = int(coord.y)
        # draw a larger circle for the note
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 0, 0))  # Red for notes
        

    image.show()

    return image
"""

def get_note_position(note, c1: Vector2, c2: Vector2, c3: Vector2, c4: Vector2, string_count=STRING_COUNT, fret_count=FRET_COUNT + 1):
    """
    Map a (string, fret) to a point on the warped quad using real guitar fret spacing.
    Ensure string positions are not on the left/right edges and fret positions are not on
    the top/bottom edges unless the fret is 0 (nut), which is allowed to be on the top edge.
    """
    # allow a direct string note "string_fret"
    if isinstance(note, str):
        try:
            s, f = note.split("_")
            note = Vector2(float(s), float(f))
        except Exception:
            pass

    if not hasattr(note, "x") or not hasattr(note, "y"):
        raise ValueError("note must be a Vector2 pixel coordinate or a 'string_fret' string")

    nx = float(note.x)
    ny = float(note.y + 1)  # shift fret by +1 to match physical fret numbering

    # Heuristic: treat as logical (string,fret) when values are in expected ranges
    if -0.5 <= nx <= (string_count + 0.5) and -0.5 <= ny <= (fret_count + 0.5):
        # compute u (string) and v (fret) in [0,1]
        # place single string in the middle
        if string_count <= 1:
            u = 0.5
        else:
            u = (nx - 0.5) / (string_count)

        # clamp string parameter to [0,1]
        u = max(0.0, min(1.0, u))

        # fret -> physical spacing using 12th-root-of-2 rule
        f = float(ny)
        # clamp fret to valid range
        f = max(0.0, min(float(fret_count), f))

        if fret_count <= 0:
            v = 0.0
        else:
            denom = 1.0 - 1.0 / (2.0 ** (fret_count / 12.0))
            if denom <= 0.0:
                lnorm = 0.0
            else:
                lnorm = (1.0 - 1.0 / (2.0 ** (f / 12.0))) / denom
            # keep previous orientation: v = 1 at nut (f=0), v = 0 at last fret
            v = 1.0 - lnorm

        # numeric safety
        v = max(0.0, min(1.0, v))

        # enforce margins: don't place on edges unless fret == 0 (nut allowed on top edge)
        EPS = 1e-4
        # always keep strings slightly inset from left/right edges
        u = max(EPS, min(1.0 - EPS, u))

        if f == 0.0:
            # allow the nut (v == 1.0) to be on the top edge
            v = min(1.0, v)
            # but avoid putting it exactly at bottom edge
            v = max(EPS, v)
        else:
            # for any non-zero fret, keep away from top/bottom edges
            v = max(EPS, min(1.0 - EPS, v))

        one_u = 1.0 - u
        one_v = 1.0 - v

        px = (one_u * one_v) * c1.x + (u * one_v) * c2.x + (one_u * v) * c3.x + (u * v) * c4.x
        py = (one_u * one_v) * c1.y + (u * one_v) * c2.y + (one_u * v) * c3.y + (u * v) * c4.y

        return Vector2(px, py)

    # Otherwise assume it's already pixel coordinates — return as floats
    return Vector2(nx, ny)