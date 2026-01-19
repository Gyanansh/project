import turtle
import math

# Screen setup
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Solar System Visualizer - Optimized")
screen.setup(width=600, height=600)
screen.tracer(0) # Turns off animation for manual updating

# Sun
sun = turtle.Turtle()
sun.shape("circle")
sun.color("yellow")
sun.shapesize(2)
sun.penup()

# Planet setup function
def create_planet(color, size, radius):
    planet = turtle.Turtle()
    planet.shape("circle")
    planet.color(color)
    planet.shapesize(size)
    planet.penup()
    
    # Draw the orbit path once
    path = turtle.Turtle()
    path.hideturtle()
    path.pencolor("gray")
    path.penup()
    path.goto(0, -radius)
    path.pendown()
    path.circle(radius)
    
    return planet

# Create planets with specific radii
earth = create_planet("blue", 0.7, 150)
mars = create_planet("red", 0.6, 220)

# Orbit radius
earth_radius = 150
mars_radius = 220

# Angle
angle = 0

# Animation loop
while True:
    angle += 0.01 # Adjusted for smoothness

    # Earth position
    earth_x = earth_radius * math.cos(angle)
    earth_y = earth_radius * math.sin(angle)
    earth.goto(earth_x, earth_y)

    # Mars position (Scientifically, Mars takes ~1.88 Earth years to orbit)
    mars_angle = angle * 0.531 
    mars_x = mars_radius * math.cos(mars_angle)
    mars_y = mars_radius * math.sin(mars_angle)
    mars.goto(mars_x, mars_y)

    screen.update() # Refresh the screen with new positions