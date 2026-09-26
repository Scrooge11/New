"""Convert a string to an SVG path using fontTools (+ HarfBuzz shaping for kerning).
Usage (module): from text2path import TextPath; tp = TextPath(font_path, axes={'wght':800}); d, width = tp.path("HELLO", size=100, tracking=0.04)
tracking is in em units (0.04 = 4% of size added between letters).
"""
import sys, io
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
try:
    import uharfbuzz as hb
except ImportError:
    hb = None

import re
_num = re.compile(r'-?\d+\.\d+')
def _round(d):
    return _num.sub(lambda m: ('%.1f' % float(m.group())).rstrip('0').rstrip('.'), d)

class TextPath:
    def __init__(self, path, axes=None):
        f = TTFont(path)
        if axes and 'fvar' in f:
            f = instancer.instantiateVariableFont(f, axes)
        self.font = f
        self.upem = f['head'].unitsPerEm
        self.glyphset = f.getGlyphSet()
        self.cmap = f.getBestCmap()
        self.hmtx = f['hmtx']
        buf = io.BytesIO(); f.save(buf); self.blob = buf.getvalue()
        self.hbfont = None
        if hb is not None:
            face = hb.Face(self.blob); self.hbfont = hb.Font(face)
        self.cap_height = getattr(f['OS/2'], 'sCapHeight', None) or 700
        self.x_height = getattr(f['OS/2'], 'sxHeight', None) or 500

    def _shape(self, text):
        """Return list of (glyph_name, x_advance, x_offset, y_offset) in font units."""
        if self.hbfont is None:
            out = []
            for ch in text:
                g = self.cmap.get(ord(ch))
                if g is None: continue
                out.append((g, self.hmtx[g][0], 0, 0))
            return out
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": True})
        order = self.font.getGlyphOrder()
        out = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((order[info.codepoint], pos.x_advance, pos.x_offset, pos.y_offset))
        return out

    def path(self, text, size=100, tracking=0.0, x=0, y=0):
        """Return (d, total_width). Baseline at y, start at x. Coordinates in px."""
        s = size / self.upem
        cur = 0.0
        cmds = []
        shaped = self._shape(text)
        for i, (g, adv, xo, yo) in enumerate(shaped):
            pen = SVGPathPen(self.glyphset)
            tpen = TransformPen(pen, (s, 0, 0, -s, x + cur + xo * s, y - yo * s))
            self.glyphset[g].draw(tpen)
            c = pen.getCommands()
            if c: cmds.append(c)
            cur += adv * s
            if i < len(shaped) - 1:
                cur += tracking * size
        return _round(' '.join(cmds)), cur

    def width(self, text, size=100, tracking=0.0):
        return self.path(text, size, tracking)[1]

if __name__ == '__main__':
    fp, txt = sys.argv[1], sys.argv[2]
    tp = TextPath(fp)
    d, w = tp.path(txt, 100)
    print(w); print(d[:200])
