from applications.games import core
import random


class Snake(core.Game):
    # Directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def random_food_location(self, width=10, height=15):
        """Spawns the food in a random location without colliding with the snake.

        Returns:
            (int, int): A location on the board that does not collide with the snake.
        """
        location = (random.randint(0, width-1), random.randint(0, height-1))
        while location in self.snake:
            location = (random.randint(0, width-1),
                        random.randint(0, height-1))
        return location

    def reset(self, io):
        # Reset the press queue. I use a queue for the button presses, so that the user can quickly
        # press for example left, down and then it would execute left in one frame and down in the next one.
        # This allows for faster and more accurate steering of the snake
        self.button_press_queue = []

        # The initial body of the snake
        self.snake = [(5, 5), (4, 5), (3, 5)]

        # The snakes goes right at the beginning
        self.direction = self.RIGHT

        # Initialize the food at some random location
        self.food = self.random_food_location(
            width=io.display.width,
            height=io.display.height
        )

        # Set speed and progression of snake. Progression accumulates the time that has passed since last movement.
        self.snake_progression = 0
        self.snake_speed = 3

    def _update_midgame(self, io, delta):
        # Check controller values. We look for fresh_values, because we only care
        # about button presses and not if the button is held down
        if io.controller.left.get_fresh_value():
            self.button_press_queue.append(self.LEFT)
        if io.controller.right.get_fresh_value():
            self.button_press_queue.append(self.RIGHT)
        if io.controller.up.get_fresh_value():
            self.button_press_queue.append(self.UP)
        if io.controller.down.get_fresh_value():
            self.button_press_queue.append(self.DOWN)

        pulser = abs(self.pulse_progression -
                     int(self.pulse_progression) - 0.5)*2

        self.snake_progression += delta * self.snake_speed
        if self.snake_progression > 1:
            self.snake_progression -= 1

            if len(self.button_press_queue) > 0:
                direction = self.button_press_queue[0]
                self.button_press_queue = self.button_press_queue[1:]
                if direction[0] != -self.direction[0] or direction[1] != -self.direction[1]:
                    self.direction = direction

            new_x = self.snake[0][0] + self.direction[0]
            if new_x >= io.display.width:
                new_x -= io.display.width
            if new_x < 0:
                new_x += io.display.width

            new_y = self.snake[0][1] + self.direction[1]
            if new_y >= io.display.height:
                new_y -= io.display.height
            if new_y < 0:
                new_y += io.display.height

            new_head = (new_x, new_y)
            if new_head in self.snake:
                self.last_score = len(self.snake)
                self.state = self.GAME_OVER
                return

            if new_head == self.food:
                self.food = self.random_food_location(
                    width=io.display.width,
                    height=io.display.height
                )
                self.snake_speed += 0.1
                self.snake = [new_head] + self.snake
            else:
                self.snake = [new_head] + self.snake[:-1]

        for x in range(io.display.width):
            for y in range(io.display.height):
                if (x, y) == self.food:
                    brightness = int(pulser * 255)
                    io.display.update(x, y, (brightness, 0, 0))
                elif (x, y) in self.snake:
                    io.display.update(x, y, (11, 116, 93))
                else:
                    io.display.update(x, y, (0, 0, 0))

    def _update_gameover(self, io, delta):
        self.snake_progression += delta * 7
        if self.snake_progression > 1:
            self.snake_progression -= 1
            if len(self.snake) > 0:
                self.snake = self.snake[1:]
            else:
                self.state = self.PRE_GAME
                return

        for x in range(io.display.width):
            for y in range(io.display.height):
                if (x, y) in self.snake:
                    io.display.update(x, y, (116, 11, 11))
                else:
                    io.display.update(x, y, (0, 0, 0))
