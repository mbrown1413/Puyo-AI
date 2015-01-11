
import puyo


class Driver(object):
    """
    Coordinates between `Controller`, `AI`, and `Vision` classes to play a game
    of Puyo Puyo.
    """

    def __init__(self, controller, ai=None, vision=None):
        """
        Args:
            controller: Instance of the `Controller` class to use to control
                the game.
            ai: Instance of the `AI` class to use to determine moves to make.
                Defaults to an instance of the `DEFAULT_AI` constant.
            vision: Instance of `Vision` class to use to recognize the game
                state. Defaults to `Vision()` with default arguments.
        """
        self.controller = controller
        self.vision = vision if vision is not None else puyo.Vision()
        if isinstance(ai, basestring):
            self.ai = puyo.AI_REGISTRY[ai]()
        elif ai is None:
            self.ai = DEFAULT_AI()
        else:
            self.ai = ai

    def step(self, img):
        """Process the given image and take action if nessesary.

        TODO: Return value?

        """
        state = self.vision.get_state(img)

        if state.new_move:
            pos, rot = self.ai.get_move(state.board.copy(), state.current_beans)
            self.controller.puyo_move(pos, rot)

        return state
