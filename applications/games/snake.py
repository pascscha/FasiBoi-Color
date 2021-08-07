from applications.games import core
from helpers import animations
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
        self.ticker = animations.Ticker(3)

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

        # Pulser value, that goes back and forth from 0 to 1, used to set brightness of food
        pulser = abs(self.pulse_progression -
                     int(self.pulse_progression) - 0.5)*2

        # Move the snake to the next field if the time is ready
        if self.ticker.tick(delta):

            # Execute next command on the button queue
            if len(self.button_press_queue) > 0:
                direction = self.button_press_queue[0]
                self.button_press_queue = self.button_press_queue[1:]
                # Check that the direction is valid. Not allowed is to change direction by 180°, e.g. from left to right
                # or from up to down.
                if direction[0] != -self.direction[0] or direction[1] != -self.direction[1]:
                    self.direction = direction

            # Calculate the new x position of the snake and warp it around the screen if necessary
            new_x = self.snake[0][0] + self.direction[0]
            if new_x >= io.display.width:
                new_x -= io.display.width
            if new_x < 0:
                new_x += io.display.width

            # Calculate the new y position of the snake and warp it around the screen if necessary
            new_y = self.snake[0][1] + self.direction[1]
            if new_y >= io.display.height:
                new_y -= io.display.height
            if new_y < 0:
                new_y += io.display.height

            # Check if there is a collision with the snakes body
            new_head = (new_x, new_y)
            if new_head in self.snake:
                # Set the score to the length of the snake and proceed to the game over state
                self.score = len(self.snake)
                self.state = self.GAME_OVER
                return

            # We found the food
            if new_head == self.food:
                # Generate new food
                self.food = self.random_food_location(
                    width=io.display.width,
                    height=io.display.height
                )
                # Increase speed of snake
                self.ticker.speed += 0.1
                # Add head of snake to body without cutting the tail by one, which increases its length by 1
                self.snake = [new_head] + self.snake
            else:
                # We did not find the food, add head to snake and cut its tail by one, so its length stays the same
                self.snake = [new_head] + self.snake[:-1]

        #
        # Draw everyting
        #

        # Fill with black
        io.display.fill((0,0,0))

        # Draw pulsating food
        food_brightness = int(pulser * 255)
        io.display.update(*self.food, (food_brightness, 0, 0))

        # Draw snake
        for (x,y) in self.snake:
            io.display.update(x, y, (11, 116, 93))
        
    def _update_gameover(self, io, delta):
        # We still use the snake progression for the dying animation
        if self.ticker.tick(delta):            
            # If the snake has still some body left, continue cutting it away
            if len(self.snake) > 0:
                self.snake = self.snake[1:]
            else:
                # When the snake is gone go back to the start screen
                self.state = self.PRE_GAME
                return

        # Fill with black
        io.display.fill((0,0,0))

        # Draw snake in red
        for (x,y) in self.snake:
            io.display.update(x, y, (116, 11, 11))
