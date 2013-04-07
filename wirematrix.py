#!/usr/bin/python2
"""

Wirematrix is a matrix screensaver that shows encoded packets captured
from the local network interface. This is extremely cool and with
time, the user learns to "see the matrix" in the encoded stream.

"""

import sys
import random

import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cairocffi as cairo

import pcap
from pyhack import GLHack


class TestGLHack(GLHack):

    def __init__(self, args):
        GLHack.__init__(self, args)
        glutInit()
        self.initGL()
        self.pcap = pcap.pcap()
        self.pcap.setnonblock()
        self.frames = 0

    def initGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDisable(GL_DEPTH_TEST)
        self.reshape(self.windowWidth, self.windowHeight)

    def init_texture(self):
        self.matrix = Matrix(self.w, self.h)

        # generate a texture id, make it current
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.texture)

        # texture mode and parameters controlling wrapping and scaling
        glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )

    def tick(self):
        for timestamp, packet in self.pcap.readpkts():
            self.matrix.column(packet)
        self.matrix.tick()

    def update_texture(self):
        self.matrix.render()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0,
                     GL_BGRA, GL_UNSIGNED_BYTE, self.matrix.data)

    def reshape(self, w, h):
        self.w, self.h = w, h
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        self.init_texture()

    def draw(self):
        self.frames += 1
        if self.frames % 10 == 0:
            self.tick()

        self.update_texture()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)        
        glPushMatrix()

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(-1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(1, 1)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(-1, 1)
        glEnd()

        glPopMatrix()

GLYPHS = [None] * 256
GLYPHS[0x00:0x20] = xrange(0x121, 0x141)
GLYPHS[0x20:0x80] = xrange(0x03, 0x63)
GLYPHS[0x80:0x100] = xrange(0xA1, 0x121)

GLYPH_W = 16
GLYPH_H = 16

class Matrix(object):
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.data = ctypes.create_string_buffer(self.h * self.w * 4)
        self.surface = cairo.ImageSurface.create_for_data(
            self.data, cairo.FORMAT_ARGB32,self.w, self.h)

        self.messages = {}

    def column(self, binary):
        # simple crowding control:
        # choose a column, if it happens to be taken - we're too crowded, throw this away
        
        maybe_free_column = random.randrange(self.w / GLYPH_W)
        if maybe_free_column not in self.messages:
            self.messages[maybe_free_column] = Message(binary, maybe_free_column, self.w, self.h)

    def tick(self):
        for message in self.messages.values():
            if not message.tick():
                del self.messages[message.x]

    def render(self):
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()

        ctx.set_operator(cairo.OPERATOR_SCREEN)
        ctx.select_font_face("cairo:monospace")
        ctx.set_font_size(14)
        
        highlights = []
        ctx.set_source_rgb(0, 255, 0)
        for message in self.messages.itervalues():
            glyphs = message.glyphs()
            ctx.show_glyphs(glyphs)
            highlights.append(glyphs[-1])
        ctx.set_source_rgb(200, 255, 200)
        ctx.show_glyphs(highlights)
        

class Message(object):
    def __init__(self, binary, x, w, h):
        self.binary = map(ord, binary)
        self.x = x
        # begin just above screen
        self.y0 = random.randrange(h / GLYPH_H / 2)
        # settle somewhere in the upper half of the screen
        self.len_exposed = 1
        self.ttl = 1
        self.screen_end_y = h / GLYPH_H

    def tick(self):
        if self.len_exposed < len(self.binary):
            self.len_exposed += 1
        elif self.ttl > 0:
            self.ttl -= 1
        else:
            self.y0 += 1
        return self.y0 <= self.screen_end_y
        
    def glyphs(self):
        return [(GLYPHS[c], GLYPH_W * self.x, GLYPH_H * (self.y0 + i))
                for i, c in enumerate(self.binary[:self.len_exposed])]


if __name__ == "__main__":
    x = TestGLHack(sys.argv)
    x.run()
