
from time import time
from collections import deque

import puyo


class Driver(object):
    """
    Coordinates between `Controller`, `AI`, and `Vision` classes to play a game
    of Puyo Puyo.
    """

    BUTTON_DELAY = 0.1

    def __init__(self, controller, ai=puyo.DEFAULT_AI_NAME, player=1, vision_cls=puyo.Vision):
        """
        Args:
            controller: Instance of the `Controller` class to use to control
                the game.
            ai: Instance of the `AI` class or subclass to use to determine
                moves to make.  If this is a string, it should be the name of an AI
                to instantiate, as defined in the `AI_REGISTRY` dictionary.
                Defaults to `DEFAULT_AI_NAME`.
            player: `1` (left player) or `2` (right player).
            vision_cls: Either the `Vision` class or a subclass. Instantiated
                and used to recognize game state.
        """
        self.controller = controller
        if isinstance(ai, basestring):
            self.ai = puyo.AI_REGISTRY[ai]()
        else:
            self.ai = ai
        self.player = player
        self.vision_cls = vision_cls
        self.vision = self._get_vision_instance()

        self.last_state = None

        self.button_queue = deque()
        self.last_button_press_time = float("-inf")

    def step(self, img):
        """Process the given image and take action if nessesary.

        TODO: Return value?

        """

        if self.button_queue:
            self._handle_button_queue()
            return self.last_state
        else:
            return self._step_normal(img)

    def _step_normal(self, img):
        state = self.vision.get_state(img)

        if state.special_state != "unknown":

            self._handle_special_state(state.special_state)
            self.vision = self._get_vision_instance()

        if state.new_move:
            pos, rot = self.ai.get_move(state.board.copy(), state.current_beans)
            self.controller.puyo_move(pos, rot)

        self.last_state = state
        return state

    def _handle_special_state(self, state):

        if state == "scenario_won":
            self.button_queue.append("start")

        elif state == "scenario_lost":
            self._spell_high_score("BOT")

        elif state == "scenario_continue":
            self.button_queue.append("start")

        else:
            raise ValueError("Unknown special state")

    def _spell_high_score(self, name):
        assert len(name) == 3
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

        for letter in name:
            dist = alphabet.index(letter)
            direction = "down"

            if len(alphabet) - dist < dist:
                dist = len(alphabet) - dist
                direction = "up"

            for i in range(dist):
                self.button_queue.append(direction)
            self.button_queue.append("a")

    def _handle_button_queue(self):
        t = time()
        if t - self.last_button_press_time >= self.BUTTON_DELAY:
            button = self.button_queue.popleft()
            self.controller.push_button(button)
            self.last_button_press_time = t

    def _get_vision_instance(self):
        return self.vision_cls(self.player)
