#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
# TODO (spayder26): COMMENT ATTRIBUTES before release

import threading # Lock used by TextSurface
import os.path # exists used by _parseFont
import sys # maxint used by _estimateFontSize2

import random

import pygame

colors = {
    'blue': (0, 0, 255),
    'pink': (255, 192, 203),
    'purple': (128, 0, 128),
    'fuchsia': (255, 0, 255),
    'lawngreen': (124, 252, 0),
    'darkgrey': (169, 169, 169),
    'crimson': (220, 20, 60),
    'white': (255, 255, 255),
    'navajowhite': (255, 222, 173),
    'cornsilk': (255, 248, 220),
    'bisque': (255, 228, 196),
    'palegreen': (152, 251, 152),
    'brown': (165, 42, 42),
    'darkturquoise': (0, 206, 209),
    'darkgreen': (0, 100, 0),
    'darkgoldenrod': (184, 134, 11),
    'mediumorchid': (186, 85, 211),
    'chocolate': (210, 105, 30),
    'darkorange': (255, 140, 0),
    'papayawhip': (255, 239, 213),
    'olive': (128, 128, 0),
    'darksalmon': (233, 150, 122),
    'peachpuff': (255, 218, 185),
    'plum': (221, 160, 221),
    'slategrey': (112, 128, 144),
    'mintcream': (245, 255, 250),
    'cornflowerblue': (100, 149, 237),
    'hotpink': (255, 105, 180),
    'darkblue': (0, 0, 139),
    'limegreen': (50, 205, 50),
    'deepskyblue': (0, 191, 255),
    'darkkhaki': (189, 183, 107),
    'lightgrey': (211, 211, 211),
    'yellow': (255, 255, 0),
    'lightsalmon': (255, 160, 122),
    'mistyrose': (255, 228, 225),
    'sandybrown': (244, 164, 96),
    'deeppink': (255, 20, 147),
    'seashell': (255, 245, 238),
    'tan': (210, 180, 140),
    'aliceblue': (240, 248, 255),
    'darkcyan': (0, 139, 139),
    'darkslategrey': (47, 79, 79),
    'greenyellow': (173, 255, 47),
    'darkorchid': (153, 50, 204),
    'lightgoldenrodyellow': (250, 250, 210),
    'olivedrab': (107, 142, 35),
    'chartreuse': (127, 255, 0),
    'peru': (205, 133, 63),
    'orange': (255, 165, 0),
    'rosybrown': (188, 143, 143),
    'wheat': (245, 222, 179),
    'lightcyan': (224, 255, 255),
    'lightseagreen': (32, 178, 170),
    'blueviolet': (138, 43, 226),
    'lightslategrey': (119, 136, 153),
    'cyan': (0, 255, 255),
    'mediumpurple': (147, 112, 216),
    'midnightblue': (25, 25, 112),
    'gainsboro': (220, 220, 220),
    'paleturquoise': (175, 238, 238),
    'gray': (128, 128, 128),
    'mediumseagreen': (60, 179, 113),
    'moccasin': (255, 228, 181),
    'ivory': (255, 255, 240),
    'darkslateblue': (72, 61, 139),
    'beige': (245, 245, 220),
    'green': (0, 128, 0),
    'slateblue': (106, 90, 205),
    'teal': (0, 128, 128),
    'azure': (240, 255, 255),
    'lightsteelblue': (176, 196, 222),
    'dimgrey': (105, 105, 105),
    'magenta': (255, 0, 255),
    'antiquewhite': (250, 235, 215),
    'skyblue': (135, 206, 235),
    'ghostwhite': (248, 248, 255),
    'mediumturquoise': (72, 209, 204),
    'floralwhite': (255, 250, 240),
    'lavenderblush': (255, 240, 245),
    'seagreen': (46, 139, 87),
    'lavender': (230, 230, 250),
    'blanchedalmond': (255, 235, 205),
    'darkolivegreen': (85, 107, 47),
    'darkseagreen': (143, 188, 143),
    'springgreen': (0, 255, 127),
    'navy': (0, 0, 128),
    'orchid': (218, 112, 214),
    'salmon': (250, 128, 114),
    'indianred': (205, 92, 92),
    'snow': (255, 250, 250),
    'steelblue': (70, 130, 180),
    'mediumslateblue': (123, 104, 238),
    'black': (0, 0, 0),
    'lightblue': (173, 216, 230),
    'turquoise': (64, 224, 208),
    'mediumvioletred': (199, 21, 133),
    'darkviolet': (148, 0, 211),
    'darkgray': (169, 169, 169),
    'saddlebrown': (139, 69, 19),
    'darkmagenta': (139, 0, 139),
    'tomato': (255, 99, 71),
    'whitesmoke': (245, 245, 245),
    'honeydew': (240, 255, 240),
    'mediumspringgreen': (0, 250, 154),
    'dodgerblue': (30, 144, 255),
    'aqua': (0, 255, 255),
    'forestgreen': (34, 139, 34),
    'oldlace': (253, 245, 230),
    'slategray': (112, 128, 144),
    'lightgray': (211, 211, 211),
    'goldenrod': (218, 165, 32),
    'indigo': (75, 0, 130),
    'cadetblue': (95, 158, 160),
    'lightyellow': (255, 255, 224),
    'powderblue': (176, 224, 230),
    'royalblue': (65, 105, 225),
    'sienna': (160, 82, 45),
    'thistle': (216, 191, 216),
    'lime': (0, 255, 0),
    'darkred': (139, 0, 0),
    'lightskyblue': (135, 206, 250),
    'yellowgreen': (154, 205, 50),
    'lemonchiffon': (255, 250, 205),
    'aquamarine': (127, 255, 212),
    'lightcoral': (240, 128, 128),
    'darkslategray': (47, 79, 79),
    'coral': (255, 127, 80),
    'khaki': (240, 230, 140),
    'burlywood': (222, 184, 135),
    'mediumblue': (0, 0, 205),
    'lightslategray': (119, 136, 153),
    'red': (255, 0, 0),
    'silver': (192, 192, 192),
    'palevioletred': (216, 112, 147),
    'firebrick': (178, 34, 34),
    'violet': (238, 130, 238),
    'grey': (128, 128, 128),
    'lightgreen': (144, 238, 144),
    'linen': (250, 240, 230),
    'orangered': (255, 69, 0),
    'palegoldenrod': (238, 232, 170),
    'dimgray': (105, 105, 105),
    'maroon': (128, 0, 0),
    'lightpink': (255, 182, 193),
    'mediumaquamarine': (102, 205, 170),
    'gold': (255, 215, 0)
    }

class TextSurface(pygame.Surface):
    '''TextSurface draws formatted text into its own surface.

    Properties:
        text: Text will be drawed on surface, every time is changed is
              inmediately redrawed.
        linesep: Character will be used for separate lines. Defaults to '\n'.
    '''

    _text = ""

    @property
    def text(self): return self._text

    @text.setter
    def text(self, x):
        if x is None:
            self._text = ""
            self.refresh()
        else:
            lines1 = self._text.split(self._linesep) if self._text else ()
            lines2 = x.split(self._linesep) if x else ()
            last_common_line = min(len(lines1),len(lines2))
            for i in xrange(last_common_line):
                if lines1[i] != lines2[i]:
                    last_common_line = i
                    break
            self._text = x
            self.refresh(last_common_line)

    _linesep = "\n"
    @property
    def linesep(self): return self._linesep

    @linesep.setter
    def linesep(self, x):
        self._linesep = x
        self.refresh()

    def get_text_height(self):
        '''Get text heights, in other words, the minimum surface height for
        showing all text.

        Return:
            Text height in pixels as integer.
        '''
        return self._text_height

    def get_text_width(self):
        '''Get text width, in other words, the minimum surface width for
        showing all text. This method is useless whith justified text.

        Return:
            Text width in pixels as integer.
        '''
        return self._text_width

    def __init__(self, text, size, wrap=True, linesep="\n", flags=pygame.SRCALPHA):
        '''Initializes TextSurface.

        Arguments:
            text:    Text string. If None no text will be rendered.
            size:    Surface size tuple.
            wrap:    If text will be wrapped to width or not (True by default).
            linesep: Charater for ending lines (UNIX '\n' by default).
            flags:   pygame.Surface flags (pygame.SCRALPHA by default).

        Formated multiline text is allowed.
        You can set multiple colors, font backgrounds, fonts and sizes on
        the same text, and adjust, center, or align lines if wrapping.
        Format is bbCode like:

        [fDroid Sans][s32][cblue]Blue text using Droid Sans at 32[/f][/s][/c]
        [j][c#f00]This text will be justified and red[/c][/j]

        Format options:
          r - align line to right
          l - align line to left
          c - center line
          j - justify line
          b - bold text
          u - underline
          i - italic

        Font options:
          fNAME - render text using given font
                * NAME can be either a system font name or a filename), if not
                  available default pygame font will be used.
          sSIZE - font size
                * SIZE as integer

        Color options:
          cCOLOR - text color (COLOR see below)
          bCOLOR - text background color
                 * COLOR can be an hex value line #55F or #5555FF, as rgb like
                   128,128,255 or a color name string like darkturquoise.

        Misc:
          mID - makes a pygame.Rect list, with the same position and size of
                the sorrounded text, available via TextSurface.mrects and
                TextSurface.mrect methods.
                These rects are is relative to surface, but you can change this
                using mrects_move method.
                Note everytime you change the text or call the resize methods,
                rects that represents clickable areas of text could change,
                but mrect lists keeps the reference.
              * ID identifier of de rect list
        '''
        pygame.Surface.__init__(self, size, flags=flags)

        self._rects = {}
        self._mids_by_line = {}
        self._unclosed_props = []

        self._font_cache = {} # used by parseText
        self._offset = (0,0)
        self._lock = threading.Lock()
        self._wrap = wrap
        self._linesep = linesep

        self._text_height = 0
        self._text_width = 0

        self._lineheights = ()
        if text: self.text = text

    _rects = None
    def mrect(self, identifier):
        '''Get mrects' (rects of text using [mID] tag) list referenced by
        given identifier.

        Arguments:
            identifier: String identifier as used on [mID] tag.

        Returns:
            List of pygame.Rects, relative to surface position or relative to
            last position given to TextSurface.mrects_move method, referenced
            to given identifier, if identifier not in text empty list will be
            returned (but this list keeps reference too).

        Note: List keeps its reference, so if you want to iterate for event
        handling, the list always will be updated.
        '''
        if identifier not in self._rects: self._rects[identifier] = []
        return self._rects[identifier]

    def mrects(self):
        '''Get mrects (rects of text using [mID] tag) dictionary.

        Returns:
            Dict of mrect's identifiers as keys and mrects as pygame.Rect
            lists.

        Note: Once a list of mrect's is created it will never be removed, so
        if you're thinking about using a TextSurface for rendering different
        texts with a lot of mrects, keep in mid this dictionary will grow and,
        eventually, will spend your ram with empty lists. Use this method for
        preventing this potential memory leak removing unnecesary dict keys.
        '''
        return self._rects

    def mrects_move(self, offset):
        '''Makes mrects (rects of text using [mID] tag) relative to given
        position.

        Arguments:
            offset: Tuple of coords (x,y) which will be the new reference point
                    for mrects.

        NOTE: If mrects are updated with surface's position calling this method
        when position is changed, rects will be always absolute, and safe to
        use for event handling. If (0,0) is given, rects will become relative
        to surface position.
        '''
        new = (offset[0],offset[1])
        old = self._offset
        for i in self._rects.itervalues():
            for j in i:
                j.x += new[0] - old[0]
                j.y += new[1] - old[1]
        self._offset = new

    _text_height = 0
    _text_width = 0
    def get_text_size(self):
        '''Gets width and height of rendered text.

        Returns:
            Tuple as (width, height).

        NOTE: If text if wrapped, width will be surface's width unless a line
        contains a very long word.
        '''
        return (self._text_width, self._text_height)

    _font_cache = None
    def refresh(self, linestart=0):
        '''Redraws all text to surface and update mrects.
        It's performed automatically when text is asigned or modified.

        Arguments:
            linestart:  and integer representing the line number on which
                        render starts.
        '''
        width, height = self.get_size()

        if linestart == 0:
            self._unclosed_props[:] = ()
            self._mids_by_line.clear()
            text = self._text
            py = 0
            lineheights = list()
            pygame.Surface.fill(self, (0,0,0,0))
        else:
            self._unclosed_props[:] = self._unclosed_props[:linestart]
            for i in xrange(linestart, len(self._unclosed_props)):
                if i in self._mids_by_line: del self._mids_by_line[i]

            text = "%s%s" % (
                self._unclosed_props[linestart-1],
                self._linesep.join(self._text.split(self._linesep)[linestart:]))

            py = sum(self._lineheights[:linestart])
            lineheights = list(self._lineheights[:linestart])

            if py < height:
                pygame.Surface.fill(self, (0,0,0,0),
                    pygame.Rect(0, py, width, height-py))

        text_width  = width if self._wrap else 0
        text_height = py

        rects = {}

        used_fonts = set()

        len_lineheights = len(lineheights)
        len_unclosed = len(self._unclosed_props)
        for line, size, is_justified, text_line_number, unclosed_props in parseText(
          text, width if self._wrap else 0, self._font_cache, used_fonts,
          self._linesep):

            if size[0] > text_width: text_width = size[0]
            text_height += size[1]

            line_number = text_line_number + linestart

            if line_number < len_lineheights:
                lineheights[line_number] += size[1]
            else:
                lineheights.append(size[1])
                len_lineheights += 1

            if line_number >= len_unclosed:
                self._unclosed_props.append(unclosed_props)
                len_unclosed += 1

            if py < height: # We do not need to draw beyond surface or before modifications
                py += size[1]
                if is_justified:
                    # Every word is a block if line is justified, cos every word is spaced
                    if len(line) > 1:
                        bs = (width-size[0])/(len(line)-1)
                        bsr = (width-size[0])%(len(line)-1) + bs
                    else: bs = bsr = 0
                    align = "j"
                else:
                    # Every line is a block (faster due less iterations)
                    bs = bsr = 0
                    align = tuple(j[0][0][2]["a"] for j in line if j and "a" in j[0][0][2])
                    align = "l" if not align else align[0]
                px = ((width-size[0]) if align == "r" else
                      (width-size[0])/2.+1 if align == "c" else 0)
                if line:
                    ll = len(line)
                    for j in xrange(ll):
                        for elm in line[j]:
                            props, text = elm
                            font, color, draw = props
                            if j > 0: px += draw["p"]/2
                            r = (font.render(text, True, color["c"],
                                    color["b"]) if "b" in color else
                                font.render(text, True, color["c"]))
                            w, h = r.get_size()

                            if "o" in draw: # TODO (spayder26): It's not working!
                                r.set_alpha(draw["o"])
                            self.blit(r, (px, py-h))

                            if "m" in draw:
                                mid = draw["m"]
                                rect = (px+self._offset[0],py-h+self._offset[1],w,h)
                                if mid in rects: rects[mid].append(rect)
                                else: rects[mid] = [rect]
                                if line_number in self._mids_by_line:
                                    self._mids_by_line[line_number].add(mid)
                                else:
                                    self._mids_by_line[line_number] = set((mid,))
                            del r
                            px += w + draw["p"]/2
                        px += (bsr if j == ll-1 else bs)
                        if px > width: break
            else: # Action rects must be handled
                for block in line:
                    for elm in block:
                        if "m" in elm[0][2]:
                            mid = elm[0][2]["m"]
                            if not mid in rects: rects[mid] = ()
                            if line_number in self._mids_by_line:
                                self._mids_by_line[line_number].add(mid)
                            else:
                                self._mids_by_line[line_number] = set((mid,))

        for i in tuple(key for key in self._font_cache.iterkeys() if key not in used_fonts):
            del self._font_cache[i]

        self._lock.acquire()
        used_rects = tuple(i for j in self._mids_by_line.itervalues() for i in j)

        for key, value in self._rects.iteritems():
            if key not in used_rects: value[:] = ()

        for key, value in rects.iteritems():
            if key in self._rects:
                self._rects[key][:] = (pygame.Rect(*j) for j in value)
            else:
                self._rects[key] = [pygame.Rect(*j) for j in value]

        self._lineheights = tuple(lineheights)
        self._text_width = text_width
        self._text_height = text_height
        self._lock.release()

    def copy(self):
        '''Get copy of this TextSurface.

        Returns:
            TextSurface rendered copy.
        '''
        tr = TextSurface(None, self.get_size(), flags=self.get_flags())
        tr._wrap = self._wrap
        tr._font_cache = self._font_cache.copy()
        tr._rects = dict((key, list(value)) for key, value in self._rects.iteritems())
        tr._mids_by_line = self._mids_by_line.copy()
        tr._unclosed_props = list(self._unclosed_props)
        tr._offset = self._offset
        tr._text = self._text
        tr._text_height = self._text_height
        tr._text_width = self._text_width
        tr._lineheights = self._lineheights


        tr.set_alpha(self.get_alpha())
        tr.blit(self,(0,0)) # Copying surface
        return tr

    def resize(self, w, h):
        '''Get a resized copy of this surface (useful when wrapping text).

        Args:
            w: New width int
            h: New height  int

        Returns:
            TextSurface rendered copy with given size.
        '''
        if (w, h) == self.get_size(): return self.copy()
        tr = TextSurface(None, (w, h), flags=self.get_flags())
        tr._wrap = self._wrap
        tr._rects = self._rects # We need copy rects before updating
        tr._mids_by_line = self._mids_by_line
        tr._unclosed_props = self._unclosed_props
        tr._offset = self._offset
        tr._font_cache = self._font_cache
        tr._text = self._text # Cos we don't want font_cache flushing
        tr._text_height = self._text_height
        tr._text_width = self._text_width
        tr._lineheights = self._lineheights
        tr.refresh()
        tr.set_alpha(self.get_alpha())
        return tr


def _parse_single_font_name(name, size):
    if os.path.exists(name): return pygame.font.Font(name, size)
    matched = pygame.font.match_font(name)
    if matched: return pygame.font.Font(matched, size)
    return None

def parseFont(font_names, size):
    '''Get pygame.font.Font object for given font name or font filename and
    size.

    Arguments:
        font_names: None, font name, or comma separated font names or paths.
        size:       desired font size.

    Returns:
        pygame.font.Font object for given font, or pygame default's one.
    '''
    if font_names:
        if not "," in font_names: # If single font name is given
            tr = _parse_single_font_name(font_names.strip(), size)
            if tr: return tr
        elif not "\," in font_names: # If no escaped separators are given
            for name in font_names.split(","):
                tr = _parse_single_font_name(name.strip(), size)
                if tr: return tr
        else:
            for pre_name in font_names.replace("\,","\0").split(","):
                tr = _parse_single_font_name(pre_name.replace("\0",",").strip(), size)
                if tr: return tr
    return pygame.font.Font(None, size)

def parseColor(c):
    '''Convert between a color in RGB comma separated format, hex RGB or color
    name string (as CSS standard) to RGB color tuple.
    If color cannot be parsed ValueError is raised.

    Arguments:
        c: Color string in comma separated RGB (like "255,255,255"), hex RGB
           (like "#FFF" or "#FFFFFF") or color name (like "white").

    Returns:
        Tuple of length 3 containing RGB components as int.

    Available color names:
        Aliceblue, antiquewhite, aqua, aquamarine, azure, beige, bisque, black,
        blanchedalmond, blue, blueviolet, brown, burlywood, cadetblue,
        chartreuse, chocolate, coral, cornflowerblue, cornsilk, crimson, cyan,
        darkblue, darkcyan, darkgoldenrod, darkgray, darkgreen, darkgrey,
        darkkhaki, darkmagenta, darkolivegreen, darkorange, darkorchid,
        darkred, darksalmon, darkseagreen, darkslateblue, darkslategray,
        darkslategrey, darkturquoise, darkviolet, deeppink, deepskyblue,
        dimgray, dimgrey, dodgerblue, firebrick, floralwhite, forestgreen,
        fuchsia, gainsboro, ghostwhite, gold, goldenrod, gray, green,
        greenyellow, grey, honeydew, hotpink, indianred, indigo, ivory, khaki,
        lavender, lavenderblush, lawngreen, lemonchiffon, lightblue,
        lightcoral, lightcyan, lightgoldenrodyellow, lightgray, lightgreen,
        lightgrey, lightpink, lightsalmon, lightseagreen, lightskyblue,
        lightslategray, lightslategrey, lightsteelblue, lightyellow, lime,
        limegreen, linen, magenta, maroon, mediumaquamarine, mediumblue,
        mediumorchid, mediumpurple, mediumseagreen, mediumslateblue,
        mediumspringgreen, mediumturquoise, mediumvioletred, midnightblue,
        mintcream, mistyrose, moccasin, navajowhite, navy, oldlace, olive,
        olivedrab, orange, orangered, orchid, palegoldenrod, palegreen,
        paleturquoise, palevioletred, papayawhip, peachpuff, peru, pink, plum,
        powderblue, purple, red, rosybrown, royalblue, saddlebrown, salmon,
        sandybrown, seagreen, seashell, sienna, silver, skyblue, slateblue,
        slategray, slategrey, snow, springgreen, steelblue, tan, teal, thistle,
        tomato, turquoise, violet, wheat, white, whitesmoke, yellow and
        yellowgreen.
    '''
    try:
        if c[0] == "#":
            if len(c)==4: return (int(c[1]*2,16),int(c[2]*2,16),int(c[3]*2,16))
            elif len(c)==7: return (int(c[1:3],16),int(c[3:5],16),int(c[5:7],16))
        elif c.count(",") == 2:  return tuple(int(i) for i in c.split(","))
        elif c.lower() in colors: return colors[c.lower()]
    except: pass
    raise ValueError("Unknown color: %s" % c)


def parseProp(prop, font_cache = None, used_fonts = None):
    '''Parses a text property (those sorrounded by '[' and ']') and returns
    a font and format tuple.

    Arguments:
        prop: format string.
        font_cache: optional dictionary whose keys are font names and values
                    are pygame.font.Font instances.
        used_fonts: optional set of font names.

    Returns:
        3d tuple as (pygame.font.Font instance, text color, draw hints' dict).
        Text color is provided as a rgb 3d tuple as (red, green, blue) and
        draw hints' dictionary are data will be used for rendering and blitting
        the text onto a surface.
        '''
    name = None
    size = 24
    bold = italic = underline = False
    color = {"c":(255,255,255)}
    draw = {}
    for i in prop:
        if i == "b": bold = True
        elif i == "i": italic = True
        elif i == "u": underline = True
        elif i in "lrjc": draw["a"] = i
        elif i[0] == "m": draw["m"] = i[1:]
        elif i[0] == "e": draw["e"] = int(i[1:]) # TODO: MARGINS
        elif i[0] == "o": draw["o"] = int(i[1:])
        elif i[0] == "s": size = int(i[1:])
        elif i[0] == "f": name = None if i[1:] == "None" else i[1:]
        elif i[0] in "cb": color[i[0]] = parseColor(i[1:])
    f = (name, size, bold, italic, underline)
    if font_cache and f in font_cache:
        font, t = font_cache[f]
        if not used_fonts is None: used_fonts.add(f)
    else:
        font = parseFont(name, size)
        font.set_bold(bold)
        font.set_italic(italic)
        font.set_underline(underline)
        test = "THX 348: It's a rare movie." # test string to calc extra space
        base = font.size(test)[0]
        l = len(test)-1
        t = 0.
        for i in xrange(1,l):
            t += base - font.size(test[0:i])[0] - font.size(test[i:])[0]
        t = t/l
        if not font_cache is None: font_cache[f] = (font, t)
        if not used_fonts is None: used_fonts.add(f)
    draw["p"] = t
    return (font, color, draw)


def _sizeElement(element):
    props, text = element
    w, h = props[0].size(text)
    l =  props[0].get_linesize()
    return w, h, l


def _boundElement(element, width, previous=None):
    props, text = element
    font = props[0]
    lh = font.get_linesize()
    w, h = font.size(text)
    drop_last = False
    if w < width: return element, None, width - w, drop_last
    ntext = []
    while w > width:
        p = text.rfind(" ")
        if p == -1: break
        ntext.append(text[p:])
        text = text[:p]
        w = font.size(text.rstrip())[0]
    if ntext and ntext[-1] == " ":
        # Removing last added spaces (newlines cannot start with spaces).
        p = -1
        l = -len(ntext)-1
        while p>l and ntext[p] == " ": p -= 1
        ntext = ntext[:p+1]
    if ntext and not text and previous is None:
        # We cannot drop first word of line
        text = ntext.pop()
        w = font.size(text.rstrip())[0]
    rw = width - w
    if rw < 0 and previous: drop_last = True
    if ntext:
        ntext.reverse()
        ntext = "".join(ntext).lstrip()
    if text: text = text.rstrip()
    return ((props, text) if text else None), ((props, ntext) if ntext else None), rw, drop_last

counter1 = 0
def _estimateFontSize(text, size, font_size, font_cache, decreasing = False):
    #global counter1
    #counter1 += 1


    linewidth = 0
    lineheight = 0
    for stuff, line_size, j in parseText("[s%d]%s" % (font_size, text), font_cache=font_cache):
        if line_size[0] > linewidth: linewidth = line_size[0]
        lineheight += line_size[1]

    if linewidth > size[0] or lineheight > size[1]:
        if not decreasing: print "!!! %d" % font_size
        #else: print "<<< %d" % font_size
        if font_size == 1: return 0
        return _estimateFontSize(text, size, font_size-1, font_cache, True)
    elif decreasing:
        #print "<<< %d" % font_size
        return font_size
    #print ">>> %d" % font_size
    return _estimateFontSize(text, size, font_size+10, font_cache)

counter2 = 0
def _estimateFontSize2(text, size, value, step, bigger, lower, font_cache):
    #global counter2
    #counter2 += 1

    linewidth = 0
    lineheight = 0
    for stuff, line_size, isj, lno, ucp in parseText(
      "[s%d]%s" % (value, text),
      font_cache=font_cache):
        if line_size[0] > linewidth:
            linewidth = line_size[0]
        lineheight += line_size[1]

    #print lower, bigger, "%d?" % value

    if linewidth > size[0] or lineheight > size[1]:
        next_step = step/2 if step > 2 else 1
        next_value = value - next_step
        if next_value == lower:
            return next_value
        if value < bigger:
            bigger = value
    elif bigger < sys.maxint:
        next_step = step/2 if step > 2 else 1
        next_value = value + next_step
        if next_value == bigger:
            return value
        if value > lower:
            lower = value
    else:
        next_step = step*2
        next_value = value + next_step
        if value > lower:
            lower = value

    return _estimateFontSize2(text, size, next_value, next_step, bigger, lower, font_cache)

def estimateFontSize(text, size):
    #global counter1, counter2
    '''Estimate the maximun font size for a given text on a given size.

    Arguments:
        text:  text
        size:  2d tuple as (width, height)

    Returns:
        The maximum font size as integer.
    '''
    st = text.strip()
    if st.startswith("[s"):
        end = st.rfind("[/s]", 2)
        if end == -1 or end == len(st)-4:
            return int(st[2:st.find("]", 2)])

    if text:
        #tr = _estimateFontSize2(text, size, 10, font_cache)
        #print tr, counter1
        #counter1 = 0
        #return tr

        #tr = _estimateFontSize2(text, size, 10, 10, sys.maxint, -1, font_cache)
        #print tr, counter2
        #counter2 = 0
        #return tr
        return _estimateFontSize2(text, size, 10, 10, sys.maxint, -1, {})
    return 0


def parseText(text, width=0, font_cache=None, used_fonts=None, linesep="\n"):
    '''Receives a text and an optional width (for line wrapping) and returns
    an iterator.

    Arguments:
        text:       formatted text string.
        width:      maximum line width for text wrapping, if 0 no text is
                    wrapped. Defaults to 0.
        font_cache: an optional dict will be used for pygame.Font cache.
                    Dictionary keys will be a tuple as
                    (font name, font size, bold, italic, underlined)
        used_fonts: an optional set of fonts for keeping track of font_cache
                    used fonts, storing its keys.
        linesep:    character used for line endings. Defaults to '\n'.

    Yields:
        Every iterator result a tuple as (line, size, is_justified, text_line).
        Size is the line width and height in pixels and line is a list
        containing tuples as (format_data, text). 'format_data' is a 2d tuple
        as (pygame.Font object, format_properties dictionary).
        Note that text line is provided because the lines from the given text
        may differ from the yielded ones when wrapping.
    '''
    if not pygame.font.get_init(): pygame.font.init()
    if font_cache is None: font_cache = {}
    prop_stack = []
    content = ""
    cline = []
    lineheight = 0
    line_no = 0
    for i in text.split(linesep):
        del cline[:]
        scaped = False
        first = True
        for j in i.split("["):
            if first:
                first = False
                content += j
            elif scaped:
                scaped = False
                content = content[:-1] + "[" + j
            else:
                if content:
                    cline.append((parseProp(prop_stack, font_cache,
                      used_fonts), content))
                    content = ""
                closing = False
                prop = j.strip()[0]
                if prop == "/":
                    closing = True
                    prop = j.strip()[1]
                    for k in xrange(len(prop_stack)-1,-1,-1):
                        if prop_stack[k][0]==prop:
                            prop_stack.pop(k)
                            break
                f = j.find("]")
                if not closing: prop_stack.append(j[:f])
                content = j[f+1:]
            if j and j[-1] == "\\": scaped = True
        if content:
            cline.append((parseProp(prop_stack, font_cache, used_fonts),
              content))
            content = ""
        if width: # If fixed width (line-wrapping)
            current_line = tuple(cline)
            next_line = None
            while current_line is not None:
                j = 0
                rw = width
                ll = len(current_line)
                last = None
                justified = False

                # Line wrap
                while j < ll:
                    if not justified and "a" in current_line[j][0][2] \
                       and current_line[j][0][2]["a"] == "j":
                        justified = True
                    line, nline, rw, dl =  _boundElement(current_line[j], rw, last)
                    last = line
                    if dl:
                        # Check if we can cut down a previous block
                        break_pos = -1
                        for k in xrange(j-1, -1, -1):
                            if " " in current_line[k][1]:
                                break_pos = k
                                break
                        if break_pos > -1:
                            bp, bt = current_line[break_pos]
                            bt = (bt[:bt.rfind(" ")], bt[bt.rfind(" ")+1:])
                            next_line = ((bp,bt[1].lstrip()),)+current_line[break_pos+1:]
                            current_line = current_line[:break_pos] + ((bp,bt[0]),)
                            break
                    if nline:
                        next_line = (nline,)+current_line[j+1:]
                        if line: current_line = current_line[:j] + (line,)
                        else: current_line = current_line[:j]
                        break
                    j += 1

                # Justify if j prop is in line and line isn't last
                must_justify = justified and next_line

                # Block formatting
                current_line = (
                    tuple(((props, word),) for props, text in current_line
                        for word in text.split(" ") if word)
                    if must_justify else tuple((current_line,)) if ll else ())

                # Linesize calc (after block formatting due JLine stuff)
                linewidth = 0
                if current_line: lineheight = 0
                for block in current_line:
                    for elm in block:
                        w, h, lh = _sizeElement(elm)
                        linewidth += w + elm[0][2]["p"]
                        #height = max(h, lh height)
                        if lh > lineheight: lineheight = lh
                yield (current_line, (linewidth, lineheight), must_justify,
                    line_no, "".join("[%s]" % prop for prop in prop_stack))
                current_line = next_line
                next_line = None
        else:
            linewidth = 0
            if cline: lineheight = 0
            for elm in cline:
                w, h, lh = _sizeElement(elm)
                linewidth += w + elm[0][2]["p"]
                #height = max(h, lh height)
                if lh > lineheight: lineheight = lh
            yield (tuple((cline,)) if cline else (), (linewidth, lineheight),
                False, line_no, "".join("[%s]" % prop for prop in prop_stack))
        line_no += 1


if __name__ == "__main__":
    import timeit
    import sys
    import random
    size = (800,600)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    state = 0
    states = colors.keys()
    text = '''
[b]Hello, world.[/b]
[fDejaVu Serif, Serif][c#FF0000]I'm a formatted[/c] text.[/f]
[fUbuntu, Sans][b][u]With diff[c#00FF00]er[/c]ent fonts[/f][fDejaVu Sans, Sans][cpurple] and[/u] colors.[/c][/f][/b]

[c]This text [o100]is[/o] centered \[ and this brackets are ] \[ scaped ][/c]

[fPurisa, Garamont, Sans][s14][j]Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse volutpat, neque sed luctus vestibulum, nulla nisl luctus turpis, et feugiat ligula diam vel orci. Praesent urna risus, pharetra sit amet mollis ut, commodo eu libero. Vivamus vestibulum velit et erat tempor at fringilla est sagittis. Vivamus ac fringilla risus. Aenean lobortis odio non arcu aliquet tristique in eget elit. Donec auctor sodales diam, in sagittis ligula elementum non. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer vitae quam orci, quis mattis justo. Duis nec elit lorem, non mattis lorem. Sed sapien turpis, rhoncus ut ultricies eu, iaculis ultrices mauris. Pellentesque magna eros, mattis a pulvinar quis, rhoncus ac justo. In accumsan, orci ut porta rhoncus, mi turpis commodo lorem, at malesuada ante est ac dolor. Vestibulum eu lorem felis. Phasellus pulvinar sodales felis a vehicula. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec nec odio nisi, sit amet malesuada dolor. Quisque tincidunt pellentesque egestas.[/j]

[r]Suspendisse vulputate, ante non scelerisque tincidunt, purus [mClickable][u][c%s]lectus eleifend metus[/c][/u][/m], aliquet ornare eros eros in turpis. Nulla aliquet pharetra pellentesque. Sed nec magna justo. Cras ac felis turpis. Praesent ut convallis purus. Curabitur eget turpis nulla. Nunc eget urna ut enim consectetur tempor. Aenean quis lacus et nisl blandit varius. Nulla facilisi. Suspendisse eget lacus vel risus elementum aliquet. Sed sagittis aliquet dui. Proin vel mi nisl, non condimentum magna. Cras id tellus a lorem gravida dignissim eget sed mi. Nam neque dolor, dictum et faucibus sed, dictum at leo. Aenean consequat metus et nisi mattis eget pulvinar orci hendrerit.[/r]'''

    ts = TextSurface(text % "blue", size)
    test_times = 100

    if True:
        def appendTs(obj, text):
            obj.text += text
        def popTs(obj, number):
            obj.text = obj.text[:-number]
        def prependTs(obj, text):
            obj.text = text + obj.text
        def pop0Ts(obj, number):
            obj.text = obj.text[number:]
        def refresh(obj):
            obj._font_cache.clear()
            obj.refresh()

        print "Benchmarking TextSurface: %d characters, %d words, %s%d lines." % (
            len(ts.text), len(ts.text.split()), "wrapped, " if ts._wrap else "",
            len(ts.text.split("\n")))
        text_to_add = "\n[b]I think this line[/f] should be removed.\n"
        len_text_to_add = len(text_to_add)
        print "Copy:   %g s" % (timeit.timeit(lambda: ts.copy(),
            number=test_times)/test_times)
        print "Render (without font cache):  %g s" % (timeit.timeit(
            lambda: refresh(ts), number=test_times)/test_times)
        print "Render (with font cache):     %g s" % (timeit.timeit(
            lambda: ts.refresh(), number=test_times)/test_times)
        print "Appending text:               %g s" % (timeit.timeit(
            lambda: appendTs(ts, text_to_add), number=test_times)/test_times)
        print "Removing text from the end:   %g s" % (timeit.timeit(
            lambda: popTs(ts, len_text_to_add), number=test_times)/test_times)
        print "Prepending text:              %g s" % (timeit.timeit(
            lambda: prependTs(ts, text_to_add), number=test_times)/test_times)
        print "Removing text from the start: %g s" % (timeit.timeit(
            lambda: pop0Ts(ts, len_text_to_add), number=test_times)/test_times)


    if False:
        print "Benchmarking font size estimation:"
        texts = (
            "[s10]Oh sorry, this is embarrasing: I've specified a font size.",
            "[fSans]What do you prefer, being [b]bold[/b] or [u]bald[/u]?",
            "Why someone would put \[s15\] on a text?",
            "[s15]Hi[/s] is like [s30]hello[/s] but shorter.")
        backends = {
            "method1":lambda text, size: _estimateFontSize(text, size, 10, {}),
            "method2":lambda text, size: _estimateFontSize2(text, size, 10, 10, sys.maxint, -1, {})
            }
        results = {}
        for test in xrange(100):
            size = (random.randint(0,100), random.randint(0,100))
            for i in texts:
                if i not in results: results[i] = {}
                for backend, fnc in backends.iteritems():
                    if backend not in results[i]: results[i][backend] = []
                    results[i][backend].append(timeit.timeit(
                        lambda:fnc(i, size),
                        number=test_times)/test_times)

        for key, values in results.iteritems():
            print key
            for backend, results in values.iteritems():
                print "\t%s %s s" % (backend, sum(j for j in results)/100)

    screen.fill(colors[states[state]])
    screen.blit(ts, (0,0))
    pygame.display.update()
    clicked_times = 0

    clickable_rects = ts.mrect("Clickable")
    while not pygame.event.peek(pygame.QUIT):
        if pygame.event.peek(pygame.VIDEORESIZE):
            event = pygame.event.get(pygame.VIDEORESIZE)[-1]
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            screen.fill(colors[states[state]])
            ts = ts.resize(*event.size)
            screen.blit(ts,(0,0))
            pygame.display.update()
        if pygame.event.peek(pygame.MOUSEBUTTONDOWN):
            event = pygame.event.get(pygame.MOUSEBUTTONDOWN)[-1]
            if pygame.Rect(event.pos, (1,1)).collidelist(clickable_rects)>-1:
                state = 0 if state >= len(colors) else state+1
                screen.fill(colors[states[state]])
                if clicked_times>0: old_text = "\n".join(ts.text.split("\n")[:-1])
                else: old_text = ts.text
                clicked_times += 1
                ts.text = "%s\nYou've clicked %d time%s." % (old_text,
                    clicked_times, "s" if clicked_times > 1 else "")
                screen.blit(ts,(0,0))
                pygame.display.update()
        pygame.event.clear()
        pygame.time.delay(16)
