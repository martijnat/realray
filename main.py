#!/usr/bin/env python2

# Copyright (C) 2017  Martijn Terpstra

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sys import stderr
from random import random
import pygame
import pygame.gfxdraw
from math import sin, cos, pi, sqrt


def main():
    pygame.init()
    size = width, height = 1024,768
    screen_ratio = width / float(height)
    screen = pygame.display.set_mode(size,pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE)
    screen.set_alpha(None)

    move_speed = 0.05
    angle_speed = 0.05

    block_size = 64
    frames_since_last_key_press = 0

    yaw = 0
    pitch = 0
    roll = 0
    # default direection vectors
    vecX = vec3(1,0,0)
    vecY = vec3(0,1,0)
    vecZ = vec3(0,0,1)
    # Camera position and relative axis.
    cameraX = vecX
    cameraY = vecY
    cameraZ = vecZ
    cameraO = vec3(0, 0, -2)

    world  = [
         # The floor is just a giant sphere
        CheckeredSphere( 0.0, -100001, 0.0,  100000, vec3(0.2, 0.2, 0.2),0.0),
        CheckeredSphere( -100003.5, 0.0, 0.0,  100000, vec3(0.2, 0.2, 0.2),0.0),
        CheckeredSphere( 0,0, 100002.5, 100000, vec3(0.2, 0.2, 0.2),0.0),


        # # 3 largest spheres in the back
        Sphere(-2,  0,  2,  1,  vec3(1,0,0)),
        Sphere( 0,  1,  2,  1,  vec3(0,1,0)),
        Sphere( 2,  0,  2,  1,  vec3(0,0,1)),
    ]

    # A single light source. Multiple light sources could be used
    sun = Light(vec3(1,8,-0.5), vec3(2,2,1).normalized())

    n = 1

    key_up =False
    key_down =False
    key_left =False
    key_right =False
    key_w =False
    key_a =False
    key_s =False
    key_d =False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    key_left = True
                elif event.key == pygame.K_RIGHT:
                    key_right = True
                elif event.key == pygame.K_UP:
                    key_up = True
                elif event.key == pygame.K_DOWN:
                    key_down = True
                elif event.key == pygame.K_w:
                    key_w = True
                elif event.key == pygame.K_a:
                    key_a = True
                elif event.key == pygame.K_s:
                    key_s = True
                elif event.key == pygame.K_d:
                    key_d = True
                elif event.key == pygame.K_ESCAPE:
                    quit(0)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    key_left = False
                elif event.key == pygame.K_RIGHT:
                    key_right = False
                elif event.key == pygame.K_UP:
                    key_up = False
                elif event.key == pygame.K_DOWN:
                    key_down = False
                elif event.key == pygame.K_w:
                    key_w = False
                elif event.key == pygame.K_a:
                    key_a = False
                elif event.key == pygame.K_s:
                    key_s = False
                elif event.key == pygame.K_d:
                    key_d = False

        if key_w:
            cameraO += cameraZ*move_speed
        if key_s:
            cameraO -= cameraZ*move_speed
        if key_a:
            cameraO -= cameraX*move_speed
        if key_d:
            cameraO += cameraX*move_speed
        if key_left:
            yaw +=angle_speed
        if key_right:
            yaw -=angle_speed
        if key_up:
            pitch +=angle_speed
        if key_down:
            pitch -=angle_speed

        # clip angles
        yaw = yaw%(2*pi)
        pitch = max(-pi,min(pi,pitch))
        # start with default direction
        vX, vY, vZ = vecX,vecY,vecZ
        # translate over yaw
        vX = (vX*cos(yaw)) +(vZ*sin(yaw))
        vZ = (vX*(-sin(yaw))) +(vZ*cos(yaw))
        # translate over pitch
        vY = (vY*cos(pitch)) +(vZ*sin(pitch))
        vZ = (vY*(-sin(pitch))) +(vZ*cos(pitch))

        cameraX = vX.normalized()
        cameraY = vY.normalized()
        cameraZ = vZ.normalized()

        if key_up|key_down|key_left|key_right|key_w|key_s|key_a|key_d:
            block_size = 64
            frames_since_last_key_press = 0
        else:
            frames_since_last_key_press +=1
            if 32*frames_since_last_key_press*(block_size*block_size) > width*height:
                block_size = max(1,block_size//2)
                frames_since_last_key_press = 0

        # screen.fill(pygame.Color(0,0,0, 255))
        for _ in range(128):
            n = (n+1)%(width*height)
            # m = (n*93703)%(width*height)
            m = (n*(width-17)*(height-17))%(width*height)
            x = m%width
            y = (m//width)%height

            y_ratio = y / float(height)
            x_ratio = x / float(width)
            p = cameraO + cameraX * (2 * x_ratio - 1.0) * screen_ratio - \
                cameraY * (2 * y_ratio - 1.0) + cameraZ * 2
            d = (p - cameraO).normalized()
            r,g,b = vec2rgb(raytrace(world, sun, cameraO, d))

            pygame.draw.rect(screen, pygame.Color(r,g,b, 255), (x,y,int(block_size),int(block_size)), 0)
        pygame.display.flip()
    pygame.quit()








def raytrace(world, sun, origin, direction, bounce_count=0):
    if bounce_count > 1:
        # For performace reasons we limit the maximum amount of bounces.
        return vec3(1,2,3).normalized()

    # Color in case the ray hits nothing
    current_color = vec3(1,2,3).normalized()
    # distance to nearest object found so far
    current_dist = float('+inf')

    for ball in world:
        if abs(origin-ball.center)>(ball.r+error):
            t = sphere_ray_collision(ball,origin,direction)
            if t>0 and t<current_dist:
                current_dist = t
                p = origin+direction*t
                color = color_mult(ball.material(p),vec3(1,2,3).normalized())
                sphere_normal = ((p - ball.center)).normalized()


                light_angle = sphere_normal.dot((sun.pos-p).normalized())
                if light_angle>0 and sun.free_path(p,world):
                    light_angle = light_angle
                    color = color + (color_mult(ball.material(p),sun.color)*light_angle)

                reflected_direction = (direction - sphere_normal*(direction.dot(sphere_normal)*(2.0))).normalized() * ball.refraction
                new_direction = (random_vector()*ball.roughness + reflected_direction*(1-ball.roughness)).normalized()
                current_color = (color*(1-ball.reflectivity)
                                 + raytrace(world,
                                            sun,
                                            origin+direction*(t-error),
                                            new_direction,
                                            bounce_count+1)*ball.reflectivity)

    return current_color

error=(2**-32)                  # used for comparisons of floats to account for rounding errors

# Vector of size 3, used for positions, direction and r,g,b color triples.
class vec3():
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "(%f, %f, %f)" % (self.x, self.y, self.z)

    def __neg__(self):
        return vec3(-self.x,
                    -self.y,
                    -self.z)

    def __add__(self, other):
        return vec3(self.x + other.x,
                    self.y + other.y,
                    self.z + other.z)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, scalar):
        return vec3(scalar * self.x,
                    scalar * self.y,
                    scalar * self.z)

    def dot(self, other):
        return sum((self.x * other.x,
                    self.y * other.y,
                    self.z * other.z))

    def normalized(self):
        s = abs(self)
        if s <= error:
            return vec3()
        return vec3(self.x / s,
                    self.y / s,
                    self.z / s)

    def __abs__(self):
        return (self.dot(self))**0.5

def random_vector():
    return vec3(-1.0+2*random(),
                -1.0+2*random(),
                -1.0+2*random())

def color_mult(c1,c2):
    return vec3(c1.x*c2.x,
                c1.y*c2.y,
                c1.z*c2.z)

def sphere_ray_collision(ball,origin,direction):
    # Find point of collision between a ray and sphere

    # Points on a ray with origin o and direction vector d are given by o+dt
    # Points on the surface of the sphere at the origin with radio r are given by p**2 - r**2 = 0
    # The intersections of these gives us (o+dt)**2 - r**2 = 0
    # This can be rewritten as (d**2)t**2 + (2do)t + (o**2-r**2) = 0

    # So we solve the quadratic equation at**2+bt+c = 0 with the following a,b and c
    a = direction.dot(direction)
    b = 2.0 * (origin-ball.center).dot(direction)
    c = (origin-ball.center).dot(origin-ball.center) - (ball.r**2)
    # We can solve this with the quadratic equation t = (-b+-sqrt(b**2-4ac)) / 2a

    # Calculate the root term
    S = (b*b)-(4*a*c)
    # If the root term is negative, there are no solutions
    if S<=error:
        return float('+inf')

    # Otherwise calculate both points
    sqrtS = S**0.5
    t1 = (-b-sqrtS)/(2.0*a)
    t2 = (-b+sqrtS)/(2.0*a)
    # return the closes point
    return min(t1,t2)

class Sphere():
    "A sphere defined by a center x,y,z and radius r"
    def __init__(self, x, y, z, r, color, reflectivity=0.3, roughness=0.1,refraction=1):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.center = vec3(x,y,z)
        self.color = color
        # fraction of light that is not taken from sphere color on hit but from a reflected raytrace
        self.reflectivity = reflectivity
        # amount by which a reflect ray is non-perfect
        self.roughness = roughness
        # Amount by which a ray changes it direction on a reflection.
        # Positive values bounce off the sphere
        # Negative values allow a ray to pass through the sphere simulating transparency
        self.refraction = refraction
    def material(self, p):
        return self.color

class CheckeredSphere(Sphere):
    """
    Spere with a custom material function to simulate a checkerboard.
    Works best where the surface normal of the sphere is close to one of
    the base vectors"""
    def material(self,p):
        patternsize = 1
        if ((p.x%(patternsize*2))>patternsize)^((p.y%(patternsize*2))>patternsize)^((p.z%(patternsize*2))>patternsize):
            return self.color
        else:
            return vec3(1,1,1)-self.color

class Light():
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
    def free_path(self,pos,world):
        for ball in world:
            t = sphere_ray_collision(ball,self.pos,(pos-self.pos).normalized())
            if t*t<(self.pos-pos).dot(self.pos-pos)-error and t*t>error:
                return False
        return True

def srgb(l):
    "Maps a color from [0,1) (linear) to [0,255] (gamma-corrected)"
    return min(255,max(0,int(l*12.92*256 if l<=0.00313066844250063 else 256*1.055*(l**(1/2.4))-0.055)))

def vec2rgb(c):
    "Given a vec3 representing a color, return a triplet of r,g,b values"
    r = srgb(c.x)
    g = srgb(c.y)
    b = srgb(c.z)
    return r,g,b

if __name__ == "__main__":
    main()
