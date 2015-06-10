
from time import time
from collections import deque

import cv2

import puyo


def _open_video(source):
    video = cv2.VideoCapture(source)

    if not video.isOpened():
        try:
            integer = int(source)
        except ValueError:
            pass
        else:
            video = cv2.VideoCapture(integer)

    if not video.isOpened():
        return None
    return video

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

    def run(self, video, video_out=None, on_special_state=None, debug=False):
        """Play the game using the given video source.

        Args:
            video: Either an OpenCV video object open with `cv2.VideoCapture`,
                or a string that can be passed to `cv2.VideoCapture`.
            video_out: Filename of AVI file to record video.
            on_special_state: What to do when the game is won or lost. Choices:
                "exit", None (just keep playing). (Default: None)
            debug: If True then show video and debug windows.

        """
        if on_special_state not in ("exit", None):
            raise ValueError('Invalid value for "on_special_state" argument')

        if debug:
            cv2.namedWindow("Frame")
            cv2.namedWindow("Grid")

        if isinstance(video, (int, basestring)):
            video_name = video
            video = _open_video(video)
            if not video:
                raise RuntimeError('Could not open video stream "{}"'.format(video_name))

        video_writer = None
        while True:

            was_read, img = video.read()

            #TODO: This is a "temporary" hacky solution for a video delay
            #      issue. I think the issue happens because of how OpenCV
            #      captures frames in a circular buffer, returning the next
            #      frame instead of the most recent one, causing the video to
            #      lag behind the actual game. This can be fixed by making the
            #      code a lot faster, but that's not always going to work.
            #      Getting 3 frames each loop iteration solves the issue, but
            #      of course skips some frames.
            was_read, img = video.read()
            was_read, img = video.read()

            if not was_read:
                print("Error: Could not read video frame!")
                break

            if debug:
                cv2.imshow("Frame", img)

            state = self.step(img)
            if on_special_state == "exit" and state.special_state != "unknown":
                return state

            if debug:
                cv2.imshow("Grid", state.board.draw())

            if video_out:
                if video_writer is None:
                    fourcc = cv2.cv.CV_FOURCC(*"I420")
                    video_writer = cv2.VideoWriter(video_out, fourcc, 25,
                                            (img.shape[1], img.shape[0]), True)
                video_writer.write(img)

            if debug:
                key = cv2.waitKey(10) % 256
                if key == 27:  # Escape
                    break

        if video_writer is not None:
            video_writer.release()

        return state

    def step(self, img):
        """Process the given image and take action if necessary.

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
