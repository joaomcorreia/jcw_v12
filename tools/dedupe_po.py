import io
from pathlib import Path


def read_blocks(lines):
    blocks = []
    current = []
    for line in lines:
        if line.strip() == "" and current:
            blocks.append(current)
            current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def block_key(block):
    msgctxt = None
    msgid = None
    in_msgctxt = False
    in_msgid = False
    for line in block:
        if line.startswith("msgctxt "):
            in_msgctxt = True
            in_msgid = False
            msgctxt = line[len("msgctxt "):].strip()
            continue
        if line.startswith("msgid "):
            in_msgid = True
            in_msgctxt = False
            msgid = line[len("msgid "):].strip()
            continue
        if line.startswith("msgid_plural "):
            in_msgid = False
            in_msgctxt = False
            continue
        if in_msgctxt and line.startswith('"'):
            msgctxt = (msgctxt or "") + line.strip()
        if in_msgid and line.startswith('"'):
            msgid = (msgid or "") + line.strip()
    return (msgctxt, msgid)


def dedupe_po(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines:
        return
    header_blocks = []
    blocks = read_blocks(lines)
    if blocks:
        header_blocks.append(blocks[0])
        blocks = blocks[1:]
    seen = set()
    kept = []
    for block in blocks:
        key = block_key(block)
        if key == (None, None):
            kept.append(block)
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(block)
    with io.StringIO() as buf:
        for block in header_blocks + kept:
            for line in block:
                buf.write(line)
            if block and not block[-1].endswith("\n"):
                buf.write("\n")
            if block is not (header_blocks + kept)[-1]:
                buf.write("\n")
        path.write_text(buf.getvalue(), encoding="utf-8")


if __name__ == "__main__":
    po_path = Path("locale/nl/LC_MESSAGES/django.po")
    dedupe_po(po_path)
