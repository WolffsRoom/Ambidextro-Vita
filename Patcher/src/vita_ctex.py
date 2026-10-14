"""Godot 4 GST2 WebP -> PNG conversion used by the native-GXM Vita port."""
import io
import struct
from PIL import Image


def convert_ctex(raw: bytes) -> bytes | None:
    if not raw.startswith(b"GST2") or len(raw) < 56:
        return None
    fmt, width, height, mips, imagefmt = struct.unpack_from("<IHHII", raw, 36)
    if fmt != 2 or imagefmt not in (0, 1, 2, 3, 4, 5):
        return None
    try:
        pos = 52
        out = bytearray(raw[:52])
        struct.pack_into("<I", out, 36, 1)
        out[19] = 12
        for i in range(mips+1):
            size = struct.unpack_from("<I", raw, pos)[0]
            pos += 4
            chunk = raw[pos:pos+size]
            pos += size
            if len(chunk) != size or chunk[:4] != b"RIFF" or chunk[8:12] != b"WEBP":
                return None
            im = Image.open(io.BytesIO(chunk))
            im.load()
            if im.size != (max(1,width>>i),max(1,height>>i)):
                return None
            im = im.convert({0:"L",1:"LA",2:"L",3:"LA",4:"RGB",5:"RGBA"}[imagefmt])
            buf = io.BytesIO()
            im.save(buf,format="PNG",optimize=True)
            blob = buf.getvalue()
            out += struct.pack("<I",len(blob)+4) + b"PNG " + blob
        if pos != len(raw):
            return None
        return bytes(out)
    except (OSError,ValueError,EOFError,IndexError,struct.error,KeyError):
        return None
