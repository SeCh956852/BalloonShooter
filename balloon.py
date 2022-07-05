import tkinter
import turtle
import random

"""
Balloon Shooter Game v1.0.0

Press up and down arrow keys to move the cannon
Press spacebar to shoot
Game finishes when the balloon is hit
"""

class App(tkinter.Tk):
    """
    Class for the tkinter application
    """

    def __init__(self) -> None:
        super().__init__()

        # set window title
        self.titleText : str = "Balloon Shooter"
        self.title(self.titleText)

        # start game
        self.createGame()
        self.start()

    def start(self) -> None:
        self.mainloop() # start tkinter event loop

    def createGame(self) -> None:
        self.Game : Game = Game(self) # create game instance


class Game:
    """
    Class for managing game state
    """

    def __init__(self, parent : App) -> None:


        self.parent : App = parent

        # frame properties of the game
        self.frameRate : int = 60
        self.framePeriod : float = 1/self.frameRate
        self.framePeriodMs : int = int(self.framePeriod * 1000)
        self.frameUpdated : bool = False

        # properties to control shooting behaviour
        self.canShoot : bool = True
        self.isShooting : bool = False
        self.shotsMissed : int = 0
        self.reloadTime : float = 0.25
        self.reloadTimeMs : int = int(self.reloadTime * 1000)

        # create canvas for drawing
        self.gameCanvas : GameCanvas = GameCanvas(self)
        self.screen : turtle.TurtleScreen = turtle.TurtleScreen(self.gameCanvas)
        self.screen.tracer(0)

        # create turtle
        self.t : turtle.RawTurtle = turtle.RawTurtle(self.screen)
        self.turtleDefault()

        # create game objects
        self.player : Player = Player(self)
        self.balloon : Balloon = Balloon(self)
        self.bullets : list = []
        self.wall : Wall = Wall(self, self.gameCanvas.canvasWidth, self.gameCanvas.canvasHeight)

        # initial render
        self.parent.after(self.framePeriodMs, self.reRender)


    def allowShoot(self) -> None:
        # allow players to shoot
        self.canShoot : bool = True


    def turtleDefault(self) -> None:
        self.t.reset() # reset turtle and drawings

        # custom default settings
        self.t.speed("fastest")
        self.t.hideturtle()


    def checkCreateBullet(self) -> None:

        # conditions when the player is not shooting
        if not self.canShoot or not self.isShooting:
            return

        # limit player's ability to shoot by one frame per second
        self.canShoot = False
        self.parent.after(self.reloadTimeMs, self.allowShoot)

        self.bullets.append(Bullet(self, self.player.x, self.player.y)) # create bullet
        

    def reRender(self) -> None:
        self.turtleDefault()

        # update game objects
        self.player.move()
        self.player.draw(self.t)

        self.balloon.move()
        self.balloon.draw(self.t)

        self.wall.draw(self.t)

        self.gameCanvas.update()

        self.checkCreateBullet() # check if the player is able to shoot, and if so, shoot

        # update every bullet instance
        bullet : Bullet
        for bullet in self.bullets:
            bullet.move()
            bullet.draw(self.t)

            # check if the bullet has hit the wall
            if bullet.checkOutOfBounds():
                self.shotsMissed += 1
                self.bullets.remove(bullet)
            
            # check if bullet has hit the balloon, and if so, end game and stop any rendering
            if bullet.checkHit():
                self.gameOverLabel = GameOverLabel(self)
                return
        
        
        self.parent.after(self.framePeriodMs, self.reRender) # set re-render after a certain period
        
        
        
class GameCanvas(tkinter.Canvas):
    """
    Class for managing the game canvas for display 
    """

    def __init__(self, parent : Game) -> None:

        self.parent : Game = parent

        # canvas dimensions
        self.canvasWidth : int = 1000
        self.canvasHeight : int = 600
        
        # initialise and display canvas
        super().__init__(
            master = self.parent.parent,
            width = self.canvasWidth,
            height = self.canvasHeight
        )

        self.pack(
            expand = True
        )


class Player:
    """
    Class for the player's cannon
    """

    def __init__(self, parent : Game) -> None:

        self.parent : Game = parent

        # player initial position
        self.x : int = 400
        self.y : int = 0

        # player geometric properties
        self.radius : int = 60
        self.cannonWidth : int = 100
        self.cannonHeight : int = 20
        self.outlineThickness : int = 2

        # player color properties
        self.color : str = "red"
        self.fillColor : str = "orange"

        
        self.speed : int = 10 # player speed when moving

        self.direction : int = 0
        

        # Move key pressed
        self.parent.parent.bind("<KeyPress-Up>", self.onUpKeyPress)
        self.parent.parent.bind("<KeyPress-Down>", self.onDownKeyPress)

        # Move key releases
        self.parent.parent.bind("<KeyRelease-Up>", self.onUpDownKeyRelease)
        self.parent.parent.bind("<KeyRelease-Down>", self.onUpDownKeyRelease)

        # Shoot key pressed
        self.parent.parent.bind("<KeyPress-space>", self.onShootKeyPress)

        # Shoot key released
        self.parent.parent.bind("<KeyRelease-space>", self.onShootKeyRelease)

        self.draw(self.parent.t) # initial draw

    def onShootKeyRelease(self, e : tkinter.Event) -> None:
        self.parent.isShooting = False

    def onShootKeyPress(self, e : tkinter.Event) -> None:
        self.parent.isShooting = True        

    def onUpKeyPress(self, e : tkinter.Event) -> None:
        self.direction : int = 1

    def onDownKeyPress(self, e : tkinter.Event) -> None:
        self.direction : int = -1

    def onUpDownKeyRelease(self, e : tkinter.Event) -> None:
        self.direction : int = 0

    def draw(self, t : turtle.RawTurtle) -> None:
        t.penup()

        # draw circle
        t.pen(
            fillcolor = self.fillColor,
            pencolor = self.color,
            pensize = self.outlineThickness
        )
        t.goto(self.x, self.y - self.radius)
        t.pendown()
        t.begin_fill()
        t.circle(self.radius)
        t.end_fill()

        # draw cannon
        t.penup()
        t.pen(
            fillcolor = "black",
            pencolor = "black"
        )
        t.goto(self.x, self.y - self.cannonHeight / 2)
        t.pendown()
        t.begin_fill()
        t.goto(self.x - self.cannonWidth, self.y - self.cannonHeight / 2)
        t.goto(self.x - self.cannonWidth, self.y + self.cannonHeight / 2)
        t.goto(self.x, self.y + self.cannonHeight / 2)
        t.goto(self.x, self.y - self.cannonHeight / 2)
        t.end_fill()
        
        t.penup()
        t.pen(
            fillcolor = "black",
            pencolor = "black",
            pensize = 1,
        )



    def move(self) -> None:

        # check if player is moving out of bounds, and if so, don't move
        if self.y + self.direction * self.speed + self.radius > self.parent.gameCanvas.canvasHeight/2 or \
        self.y + self.direction * self.speed - self.radius < -self.parent.gameCanvas.canvasHeight/2:
            return
        
        self.y = self.y + self.direction * self.speed


class Balloon:
    """
    Class for the balloon
    """

    def __init__(self, parent : Game) -> None:

        self.parent : Game = parent

        # balloon initial position
        self.x : int = -400
        self.y : int = 0

        # balloon geometric properties
        self.radius : int = 40 
        self.outlineThickness = 4

        # balloon color properties
        self.color : str = "blue"
        self.fillColor : str = "green"
        
        self.speed : int = 5 # balloon speed

        # properties for balloon movement behaviour
        self.moveFramesRemainingDefault : int = 10
        self.moveFramesRemaining : int = 0
        self.direction : int = 0

        self.draw(self.parent.t) # initial draw

    def draw(self, t : turtle.RawTurtle) -> None:
        
        t.pen(
            fillcolor = self.fillColor,
            pencolor = self.color,
            pensize = self.outlineThickness
        )

        # draw circle
        t.penup()
        t.goto(self.x, self.y - self.radius)

        t.pendown()
        t.begin_fill()
        t.circle(self.radius)
        t.end_fill()

        t.penup()
        t.pen(
            fillcolor = "black",
            pencolor = "black",
            pensize = 1,
        )


    def move(self) -> None:

        # choose a random direction after moving for for a certain amount of frames
        if self.moveFramesRemaining == 0:
            self.moveFramesRemaining = self.moveFramesRemainingDefault
            direction = random.randint(0, 1)
            
            if direction % 2 == 0:
                self.direction = 1
            else:
                self.direction = -1

        self.moveFramesRemaining -= 1

        # prevent balloon from going out of bounds
        if self.y + self.direction * self.speed + self.radius > self.parent.gameCanvas.canvasHeight/2 :
            # balloon touches top wall
            self.direction = -1
            self.moveFramesRemaining = self.moveFramesRemainingDefault

        elif self.y + self.direction * self.speed - self.radius < -self.parent.gameCanvas.canvasHeight/2:
            # balloon touches bottom wall
            self.direction = 1
            self.moveFramesRemaining = self.moveFramesRemainingDefault

        self.y += self.direction * self.speed

        

class Bullet:
    """
    Class for the bullet that the player shoots
    """

    def __init__(self, parent : Game, initialX : int, initialY : int) -> None:
        super().__init__()
        self.parent : Game = parent

        # bullet initial position
        self.x : int = initialX
        self.y : int = initialY

        # bullet geometric properties
        self.radius : int = 20
        self.outlineThickness : int = 1
        
        # bullet color properties
        self.color : str = "black"
        self.fillColor : str = "black"

        self.speed : int = self.parent.balloon.speed * 10 # bullet move speed

    def move(self) -> None:
        self.x -= self.speed

    def draw(self, t : turtle.RawTurtle) -> None:
        
        t.pen(
            fillcolor = self.fillColor,
            pencolor = self.color,
            pensize = self.outlineThickness
        )

        # draw circle
        t.penup()
        t.goto(self.x, self.y - self.radius)
        t.pendown()
        t.begin_fill()
        t.circle(self.radius)
        t.end_fill()

        t.penup()
        t.pen(
            fillcolor = "black",
            pencolor = "black",
            pensize = 1,
        )
        

    def checkOutOfBounds(self):
        # check if bullet is out of bounds
        if self.x < -self.parent.gameCanvas.canvasWidth/2:
            return True

    def checkHit(self) -> None:
        # position and geometric property of balloon
        targetX : int = self.parent.balloon.x
        targetY : int = self.parent.balloon.y
        targetRadius : int = self.parent.balloon.radius

        # get bounds of the ballooon
        targetLeft : int = targetX - targetRadius
        targetRight : int = targetX + targetRadius
        targetTop : int = targetY + targetRadius
        targetDown : int = targetY - targetRadius

        # get bounds of the bullet
        bulletLeft : int = self.x - self.radius
        bulletRight : int = self.x + self.radius
        bulletTop : int = self.y + self.radius
        bulletBottom : int = self.y - self.radius

        # check if bullet has hit the balloon
        if bulletRight > targetLeft and bulletLeft < targetRight and bulletTop > targetDown and bulletBottom < targetTop:
            return True

class Wall:
    """
    Class for the walls of the game display
    """

    def __init__(self, parent : Game, width : int, height : int) -> None:
        super().__init__()
        self.parent : Game = parent

        # wall initial position
        self.width : int = width
        self.height : int = height

        # wall geometric position
        self.wallThickness : int = 5

        self.draw(self.parent.t) # initial draw

    def draw(self, t : turtle.RawTurtle) -> None:
        
        width : int = self.width - self.wallThickness
        height : int = self.height - self.wallThickness

        # position of wall
        top : float = self.height / 2 - self.wallThickness / 2
        right : float = self.width / 2 - self.wallThickness / 2
        left : float = -right
        bottom : float = -top

        t.pensize(self.wallThickness)

        # draw wall
        t.penup()
        t.goto(right, top)
        t.pendown()
        t.goto(right, bottom)
        t.goto(left, bottom)
        t.goto(left, top)
        t.goto(right, top)
        
        t.penup()
        t.pensize(1)



class GameOverLabel(tkinter.Label):
    """
    Class for the game over label
    """

    def __init__(self, parent : Game) -> None:

        self.parent = parent

        self.text = f"Well Done! You missed {self.parent.shotsMissed} shots" # game over text

        # initialise and display label
        super().__init__(
            master = parent.parent,
            background = "#dddddd",
            text = self.text,
            font = (None, 38)
        )

        self.place(
            relx = 0.5,
            rely = 0.5,
            anchor = tkinter.CENTER
        )


if __name__ == "__main__":
    App()
