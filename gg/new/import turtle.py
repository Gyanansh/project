import turtle
import math
import time

# Screen setup
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Solar System Visualizer")
screen.tracer(0)   # smooth animation

# Sun
sun = turtle.Turtle()
sun.shape("circle")
sun.color("yellow")
sun.shapesize(2.5)
sun.penup()

# Function to create planets
def create_planet(color, size):
    p = turtle.Turtle()
    p.shape("circle")
    p.color(color)
    p.shapesize(size)
    p.penup()
    return p

# Function to draw orbit
def draw_orbit(radius):
    orbit = turtle.Turtle()
    orbit.hideturtle()
    orbit.color("gray")
    orbit.penup()
    orbit.goto(0, -radius)
    orbit.pendown()
    orbit.circle(radius)
    orbit.penup()

# Planets: name, turtle, radius, speed
planets = [
    (create_planet("gray", 0.4), 100, 1.6),   # Mercury
    (create_planet("orange", 0.5), 130, 1.3), # Venus
    (create_planet("blue", 0.7), 150, 1.0),   # Earth
    (create_planet("red", 0.6), 220, 0.8),    # Mars
    (create_planet("brown", 1.2), 280, 0.6),  # Jupiter
    (create_planet("gold", 1.0), 340, 0.5),   # Saturn
    (create_planet("lightblue", 0.9), 400, 0.4), # Uranus
    (create_planet("darkblue", 0.9), 460, 0.3)   # Neptune
]

# Draw orbits
for _, radius, _ in planets:
    draw_orbit(radius)

angle = 0

# Animation loop
while True:
    angle += 0.02

    for planet, radius, speed in planets:
        x = radius * math.cos(angle * speed)
        y = radius * math.sin(angle * speed)
        planet.goto(x, y)

    screen.update()
    time.sleep(0.01)
