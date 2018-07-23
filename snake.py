import kivy
kivy.require('1.7.2')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from random import randint

from kivy.config import Config


Config.set('graphics','resizable',0) #don't make the app re-sizeable
#Graphics fix
#this fixes drawing issues on some phones
Window.clearcolor = (0,0,0,1.) 

class WidgetDrawer(Widget):
    def __init__(self, posx, posy, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            #self.size = (10,10)
            self.rect_bg = Rectangle(pos = self.pos, size = self.size)
            self.x, self.y = posx, posy

    def update_graphics_pos(self):
        self.rect_bg.size = self.size
        self.rect_bg.pos = (self.x, self.y)
        
class SnakeHead(WidgetDrawer):
    facing = 'east'
    tile_width = NumericProperty(0)
    tile_height = NumericProperty(0)
    score = NumericProperty(0)
    speed = NumericProperty(0)

    def __init__(self, posx, posy, **kwargs):
        super().__init__(posx, posy, **kwargs)
            
    
    def move(self):
        if self.facing is 'east':
            self.x += self.speed*self.tile_width
        elif self.facing is 'west':
            self.x -= self.speed*self.tile_width
        elif self.facing is 'south':
            self.y -= self.speed*self.tile_height
        elif self.facing is 'north':
            self.y += self.speed*self.tile_height
            
    def update(self):
        self.move()

class SnakeBody(WidgetDrawer):
    pass

class Apple(WidgetDrawer):
    pass

class SnakeGame(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Window.size = (480,800)
        print(Window.width, Window.height)      
        l = Label(text = 'Snake')
        l.x = Window.width/2 - l.width/2
        l.y = Window.height*0.9
        self.add_widget(l)
        
        self.horizontal_tiles = 20
        self.vertical_tiles = 40
        self.tile_width = Window.width/self.horizontal_tiles
        self.tile_height = Window.height/self.vertical_tiles
        
        self.snake = SnakeHead(self.tile_width * (self.horizontal_tiles//3), self.tile_height * (self.vertical_tiles//3))
        self.snake.tile_width, self.snake.tile_height = self.tile_width, self.tile_height
        self.snake.size = (self.tile_width, self.tile_height)
        self.add_widget(self.snake)

        self.snakeBody = []
        for i in range(1,2):
            self.add_to_body()

        self.apple = Apple(self.tile_width * (self.horizontal_tiles//2), self.tile_height * (self.vertical_tiles//2))
        self.apple.size = (self.tile_width, self.tile_height)
        self.apple.rect_bg.source = 'apple.png'
        self.add_widget(self.apple)
        

    def add_to_body(self):
        if len(self.snakeBody) == 0:
            tmp_pos = (self.snake.x - self.snake.tile_width, self.snake.y)
        else:
            tmp_pos = (self.snakeBody[len(self.snakeBody)-1].x, self.snakeBody[len(self.snakeBody)-1].y)
        tmp = SnakeBody(tmp_pos[0],tmp_pos[1])       
        tmp.tile_width, tmp.tile_height = self.tile_width, self.tile_height
        tmp.size = (self.tile_width, self.tile_height)
        tmp.update_graphics_pos()
        self.snakeBody.append(tmp)
        self.add_widget(tmp)
        
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar':
            self.snake.speed = 0
        if keycode[1] in ('right','left','up','down'):
            self.snake.speed = 1
            if keycode[1] == 'right':
                if self.snake.facing != 'west':
                    self.snake.facing = 'east'
            elif keycode[1] == 'left':
                if self.snake.facing != 'east':
                    self.snake.facing = 'west'
            elif keycode[1] == 'down':
                if self.snake.facing != 'north':
                    self.snake.facing = 'south'
            elif keycode[1] == 'up':
                if self.snake.facing != 'south':
                    self.snake.facing = 'north'

    def moveBody(self):
        for i in range(len(self.snakeBody)-1, 0, -1):
            self.snakeBody[i].pos = self.snakeBody[i-1].pos

    def apple2snake(self):
        return (self.apple.x-self.snake.x, self.apple.y-self.snake.y)

    def snake_facing_apple(self):
        apple_snake_dist = self.apple2snake()
        print(self.snake.facing, apple_snake_dist)
        #return True
        if self.snake.facing is 'north' and apple_snake_dist == (0, self.tile_height):
            return True
        elif self.snake.facing is 'south' and apple_snake_dist == (0, -self.tile_height):
            return True
        elif self.snake.facing is 'east' and apple_snake_dist == (self.tile_width, 0):
            return True
        elif self.snake.facing is 'west' and apple_snake_dist == (-self.tile_width, 0):
            return True
        return False

    def update(self, dt):
        if self.snake.collide_widget(self.apple):
            print('snake collides with apple')
            if self.snake_facing_apple():
                print('snake should eat apple')
                self.apple.pos = (randint(0,self.horizontal_tiles-1)*self.tile_width,randint(0,self.vertical_tiles-1)*self.tile_height)
                self.snake.score += 1
                self.add_to_body()
        
        if self.snake.x > (self.horizontal_tiles-2)*self.tile_width and self.snake.facing == 'east':
            self.snake.x = (self.horizontal_tiles-1)*self.tile_width
        elif self.snake.x < self.tile_width and self.snake.facing == 'west':
            self.snake.x = 0
        elif self.snake.y > (self.vertical_tiles-2)*self.tile_height and self.snake.facing == 'north':
            self.snake.y = (self.vertical_tiles-1)*self.tile_height
        elif self.snake.y < self.tile_height and self.snake.facing == 'south':
            self.snake.y = 0
        else:
            old_pos = list(self.snake.pos)
            self.snake.update()
            if self.snake.pos != old_pos:
                self.moveBody()
                self.snakeBody[0].pos = old_pos
            

    def draw(self, dt):
        self.snake.update_graphics_pos()
        self.apple.update_graphics_pos()
        for each in self.snakeBody:
            each.update_graphics_pos()
        


class SnakeApp(App):
    def build(self):
        parent = Widget()
        game = SnakeGame()
        Clock.schedule_interval(game.draw, 1/30)
        Clock.schedule_interval(game.update, 1/10)
        parent.add_widget(game)
        return parent

if __name__ =='__main__':
    #Window.fullscreen = True
    SnakeApp().run()
