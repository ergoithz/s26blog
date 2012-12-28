#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import pygame
import zlib # svgz support

import logging
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

# SVG rendering backend detection

_bcairo = False
_bgdk = False
_bqt4 = False
_brsvg = False



try:
    # Gtk2
    if not _bcairo:
        from cairo import Context as CairoContext, \
            ImageSurface as CairoImageSurface, \
            FORMAT_ARGB32 as CairoARGB32
        _bcairo = True
except ImportError as e:
    logging.debug(e)

try:
    # Gtk3
    if not _bgdk:
        from gi.repository.GdkPixbuf import PixbufLoader as NewPixbufLoader
        from gi.repository.Gdk import cairo_set_source_pixbuf

        class GdkCairoContext(object):
            def __init__(self, base):
                self.base = base

            def __getattr__(self, x):
                return getattr(self.base, x)

            def set_source_pixbuf(self, pixbuf, x, y):
                cairo_set_source_pixbuf(self.base, pixbuf, x, y)

        PixbufLoader = NewPixbufLoader.new_with_type

        _bgdk = True
except ImportError as e:
    logging.debug(e)

try:
    # Gtk2
    if not _bgdk:
        from gtk.gdk import CairoContext as GdkCairoContext, PixbufLoader
        _bgdk   = True
except ImportError as e:
    logging.debug(e)

try:
    # Qt4
    if not _bqt4:
        from PyQt4.QtCore import QByteArray, Qt, QSize, QBuffer, QIODevice
        from PyQt4.QtSvg import QSvgRenderer
        from PyQt4.QtGui import QImage, QPainter
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        _bqt4  = True
except ImportError as e:
    logging.debug(e)

try:
    # rsvg
    if not _brsvg:
        import rsvg
        _brsvg  = True
except ImportError as e:
    logging.debug(e)

if not (_bcairo or _brsvg or _bgdk):
    raise ImportError("No SVG renderer found (cairo, rsvg, gtk or qt).")

class SVGSurface(pygame.Surface):
    '''Pygame surface for SVG rendering.'''
    _svg = None
    _size = None
    _asize = None
    _flags = 0

    @property
    def svg(self): return self._svg

    @svg.setter
    def svg(self, x):
        self._svg = x
        self.refresh()

    def __init__(self, svg, size=(None, None), flags=pygame.SRCALPHA):
        self._size = size
        self._flags = flags
        if svg:
            self._svg = svgz_decompress(svg)
            width, height = self._size
            surface = render(svg, width, height)
            self._asize = asize = surface.get_size()
            self._flags |= surface.get_flags()
            pygame.Surface.__init__(self, asize, self._flags) #, surface)
            self.blit(surface, (0,0))
        elif size:
            pygame.Surface.__init__(self, size, flags)
        else:
            raise ValueError,"size must be defined is SVG data not given."

    def refresh(self):
        '''Flush and render the svg data into current surface.'''
        surface = render(self._svg, *self._size)
        self.fill((0,0,0,0))
        self.blit(surface, (0,0))
        del surface

    def resize(self, width=None, height=None):
        '''Returns a new SVGSurface object with given width and height.

        Arguments:
            width:  new SVGSurface's width
            height: new SVGSurface's height

        Returns:
            New SVGSurface object with given width and height.'''
        tr = SVGSurface(self._svg, (width, height), self._flags)
        tr.set_alpha(self.get_alpha())
        return tr

    def resize2(self, width=None, height=None):
        '''Renders current svg object with given width and height and returns
        as pygame.Surface object.

        Arguments:
            width:  new pygame.Surface's width
            height: new pygame.Surface's height

        Returns:
            New pygame.Surface object with given width and height.
        '''
        tr = pygame.Surface((width, height), self.get_flags())
        tr.set_alpha(self.get_alpha())
        tr.blit(render(self._svg, width, height), (0, 0))
        return tr

    def copy(self):
        '''Returns a copy of current SVGSurface object.

        Returns:
            A copy of current SVGSurface object.
        '''
        size = self._asize if self._asize else self._size
        tr = SVGSurface(None, size, self._flags)
        tr._svg = self._svg
        tr.set_alpha(self.get_alpha())
        tr.blit(self,(0,0))
        return tr


class XMLTag(object):
    '''XMLTag object makes easier read and write XML tag properties, it
    provides an apply method which return modified xml string

    Properties:
        start:      Tag start position on XML string.
        namespace:  Tag XML namespace.
        tagname:    Tag XML name (without namespace).
        attributes: Attribute dictionary (keys with namespaces), do not use
                    for style, use style property instead.
        style:      Style attribute dict as in CSS.

    '''

    class _attdict(dict):
        def __setitem__(self, x, y):
            if x == "style": raise KeyError("style not allowed here")
            dict.__setitem__(self, x, y)

    @property
    def start(self): return self._startpos

    @property
    def end(self): return self._endpos

    def __init__(self, data, start=0):
        '''Constructor receives XML string and optional start position.

        Args:
            data:  xml string.
            start: integer start position of the tag in the xml string,
                   defaults to 0.
        '''
        self._data = data
        self._startpos = start
        self._endpos = data.find(">", start)+1
        self._selfclose = data[self._endpos-2] == "/"
        self.namespace = ""
        self.attributes = self._attdict()
        self.style = {}
        n = min(data.find(" ", self._startpos), data.find("\n", self._startpos))
        if n > self._endpos:
            n = (self._endpos - 2) if self._selfclose else (self._endpos - 1)
        self.tagname = data[self._startpos+1:n]
        if ":" in self.tagname:
            self.namespace, self.tagname = self.tagname.split(":")
        tag = data[n:self._endpos-1]
        while " = " in tag: tag.replace(" = ","=")
        t = None
        for i in tag.split("=\""):
            if t:
                p = i.rfind("\"")
                if t == "style": self.style.update(
                    (k.strip() for k in j.split(":"))
                    for j in i[:p].split(";"))
                else:
                    self.attributes[t] = i[:p].strip()
                t = i[p+1:].strip()
            else: t = i.strip()

    @classmethod
    def byId(self, data, identifier):
        '''Alternative constructor by id instead of start position

        Arguments:
            data:       xml string
            identifier: id attribute of tag

        Returns:
            XMLTag object or None if not found.
        '''
        pos = data.find("id=\"%s\"" % identifier)
        if pos == -1: return None
        return XMLTag(data, data.rfind("<", 0, pos))

    @classmethod
    def byTagName(self, data, tagName, namespace="", start=0):
        '''Alternative constructor by tagname instead of start position

        Arguments:
            data:    xml string
            tagName: tagname
            start:   Position from where search starts (defaults to 0).
                     this can be used for multiple tag search with same
                     tagname.

        Returns:
            XMLTag object or None if not found.
        '''
        pos = data.find(
            "<%s:%s" % (namespace, tagName) if namespace
            else"<%s" % tagName, start)
        if pos == -1: return None
        return XMLTag(data, pos)

    def update(self):
        '''Get updated tag.

        Returns:
            XML string which reflects changes made on XMLTag object
        '''
        return "<%s %s%s%s>" % (
            "%s:%s" % ( self.namespace, self.tagname) if self.namespace
            else self.tagname,
            " ".join(
                "%s=\"%s\"" % (i,j) for i, j in self.attributes.iteritems() if i != "style"),
            " style=\"%s\"" % ";".join(
                "%s:%s" % (k, v.replace("\"","'"))
                for k, v in self.style.iteritems()) if self.style
            else "",
            " /" if self._selfclose else "")


    def apply(self):
        '''Get a copy of given xml string with updated tag.

        Returns:
            XML data (as given on init) with updated tag
            .
        '''
        return "%s%s%s" % (
            self._data[:self._startpos],
            self.update(),
            self._data[self._endpos:])


def svgz_decompress(svg):
    '''Decompress svgz (gziped SVG) data string. If uncompressed data is given
    nothing is done.

    Arguments:
        svg: svgz data string.
    Returns:
        SVG data string.
        '''
    if str(svg[:3]) == "\x1f\x8b\x08": #SVGZ control chars
        svg = zlib.decompress(svg,16+zlib.MAX_WBITS) # SVGZ support
    return svg

def render(svg, width=None, height=None):
    '''Renders SVG data string to a pygame.Surface. Width and height are
    optional but both must be given for scaling.

    Arguments:
        svg: SVG or svgz data string.
        width: optional SVG width for scaling.
        height: optional SVG height for scaling.

    Returns:
        A pygame.Surface object.'''

    try:
        if _bcairo and _brsvg:
            return rsvgCairo_backend(svg, width, height)
    except BaseException as e:
        logging.debug(e)
    try:
        if _bgdk:
            return gdk_backend(svg, width, height)
    except BaseException as e:
        logging.debug(e)
    try:
        if _bcairo and _bgdk:
            return gdkCairo_backend(svg, width, height)
    except BaseException as e:
        logging.debug(e)
    try:
        if _bqt4:
            return qt4_backend(svg, width, height)
    except BaseException as e:
        logging.debug(e)
    raise RuntimeError("All available render backends failed.")

def cairo_pygame(width, height):
    '''Links pygame.Surface to a CairoContext and returns them as tuple.

    Arguments:
        width:  new pygame.Surface's width
        height: new pygame.Surface's height

    Returns:
        Returns a 2d tuple as (pygame.Surface, CairoContext).'''
    pgs = pygame.Surface((width, height), flags=pygame.SRCALPHA)
    return (pgs, CairoContext(CairoImageSurface.create_for_data(
        pygame.surfarray.pixels2d(pgs), CairoARGB32, width, height)))

def gdk_backend(data, width=None, height=None):
    '''Gdk backend for svg rendering using svg PixbufLoader.

    Arguments:
        data: SVG or svgz data string.
        width: optional width for scaling used alongside with height
        height: optional height for scaling used alongside with width

    Returns:
        A pygame.Surface object.'''
    loader = PixbufLoader("svg")
    loader.write(data)
    if width and height:
        loader.set_size(width, height)
        loader.close()
        return pygame.image.frombuffer(
            loader.get_pixbuf().get_pixels(),
            (width,height),
            "RGBA"
            )
    loader.close()
    pixbuf = loader.get_pixbuf()
    return pygame.image.frombuffer(
        pixbuf.get_pixels(),
        (pixbuf.get_width(), pixbuf.get_height()),
        "RGBA"
        )

def gdkCairo_backend(data, width=None, height=None):
    '''Gdk + cairo backend using svg PixbufLoader and cairo.Context.


    Arguments:
        data: SVG or svgz data string.
        width: optional width for scaling used alongside with height
        height: optional height for scaling used alongside with width

    Returns:
        A pygame.Surface object.'''
    loader = PixbufLoader("svg")
    loader.write(data)
    if width and height:
        loader.set_size(width, height)
    loader.close()
    pixbuf = loader.get_pixbuf()
    surface, context = cairo_pygame(pixbuf.get_width(),pixbuf.get_height())
    gdkcontext = GdkCairoContext(context)
    gdkcontext.set_source_pixbuf(pixbuf, 0, 0)
    gdkcontext.paint()
    return surface

def rsvgCairo_backend(data, width=None, height=None):
    '''rsvg + cairo backend using rsvg for rendering and cairo.Context.

    Note: This backend modifies the svg xml because rsvg doen't support
          scaling. It should affect negatively the performance but due
          rsvg fast renderering times and used SVG tag editor's optimizied
          implementation this is still the faster backend.

    Arguments:
        data: SVG or svgz data string.
        width: optional width for scaling used alongside with height
        height: optional height for scaling used alongside with width

    Returns:
        A pygame.Surface object.'''
    if width and height: # rsvg doesn't support native vector scaling
        svg = XMLTag.byTagName(svgz_decompress(data),"svg")
        sw = width/float(svg.attributes["width"])
        sh = height/float(svg.attributes["height"])
        svg.attributes["width"] = width
        svg.attributes["height"] = height
        if "transform" in svg.attributes:
            svg.attributes["transform"] += " scale(%f %f)" % (sw, sh)
        else:
            svg.attributes["transform"] = "scale(%f %f)" % (sw, sh)
        #print svg.attributes["transform"], width, height
        svg.attributes["preserveAspectRatio"] = "none"
        data = svg.apply()
        f = open("dump.svg","w")
        f.write(data)
        f.close()
    svg = rsvg.Handle(data=data)
    tr, context = cairo_pygame(svg.props.width, svg.props.height)
    svg.render_cairo(context)
    return tr

def qt4_backend(data, width=None, height=None):
    '''pyQt backend, very slow due to PyQt4 lack of interoperability.

    Arguments:
        data: SVG or svgz data string.
        width: optional width for scaling used alongside with height
        height: optional height for scaling used alongside with width

    Returns:
        A pygame.Surface object.'''
    '''raise NotImplementedError("PyQt4 SVGRenderer is buggy.")
    '''
    renderer = QSvgRenderer(QByteArray.fromRawData(data))
    if not renderer.isValid(): raise ValueError('Invalid SVG data.')
    if None in (width, height):
        size = renderer.defaultSize()
        width = width or size.width
        height = height or size.height
    img = QImage(QSize(width, height), QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    painter = QPainter(img)
    renderer.render(painter)
    painter.end()
    strio = StringIO()
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    img.save(buffer, "PNG", 0)
    strio.write(buffer.data())
    buffer.close()
    strio.seek(0)
    return pygame.image.load(strio, "PNG")


if __name__ == "__main__":
    ''' Unit test. Backends performance and Pygame window bliting. '''
    import timeit
    import time
    import os.path

    logging.getLogger().setLevel(logging.DEBUG)

    resource_dir = "../examples/resources"

    f = open(os.path.join(resource_dir, "xubuntu.svg"),"rb")
    svg = f.read()
    f.close()

    backends = (
        rsvgCairo_backend,
        gdk_backend,
        qt4_backend,
        gdkCairo_backend
        )
    pygame.display.init()
    times = 100
    trange = xrange(times)
    width = 200
    height = 200
    '''
    for j in (0.5,1,2):
        ts = {}
        errors = {}
        w = int(width * j)
        h = int(height * j)
        print("Backends performance calculation at %d%%..." % (j*100))
        for i in backends:
            ts[i] = 0
        for i in backends:
            try:
                i(svg,w,h) # For exception catching
                ts[i] = timeit.timeit(lambda: i(svg,w,h), number=times)
            except Exception as e:
                ts[i] = None
                errors[i] = e
        for i in backends:
            if ts[i] is None:
                print("    Backend %17s is not working: %s" % (
                    i.__name__, errors[i]))
            else: print("    Backend %17s, %fs" % (i.__name__, ts[i]/times))
    '''
    print("Default backend on pygame window")

    surface = pygame.display.set_mode((800,600))

    '''
    #surface.fill((255,255,255))
    mat = 0
    surface.blit(qt4_backend(svg, 800, 600),(0,0))
    pygame.display.update()
    while not pygame.event.peek(pygame.QUIT):
        pass
    '''

    surfaces = []
    tag = XMLTag.byId(svg, "circle")
    for i in xrange(0, 360, 4):
        tag.attributes["transform"] = "rotate( %d 77.5 76 )" % i
        surfaces.append(SVGSurface(tag.apply(),(800,600)))

    i = -1
    l = len(surfaces)-1
    while not pygame.event.peek(pygame.QUIT):
        pygame.event.clear()
        if i == l: i = 0
        else: i += 1
        surface.fill((0,0,0))
        surface.blit(surfaces[i],(0,0))
        pygame.display.update()
        time.sleep(0.03)
    print("Exiting...")

