import time
import turtle
t= turtle.Turtle()
turtle.title("I Love You")
screen= turtle.Screen()
screen.bgcolor("white")
t.color("red")
t.begin_fill()
t.fillcolor("pink")
t.left(140)
t.forward(180)
t.circle(-90, 200)
t.setheading(60)
t.circle(-90, 200)
t.forward(180)
t.end_fill()
t.hideturtle()
time.sleep(5)
