
import random

class PuyoAI(object):

    def move(self, board, beans):
        raise NotImplementedError("This method must be implemented by a "
                                  "subclass.")


class Puyo1DummyAI(PuyoAI):

    def move(self, board, beans):
        possible_moves = board.iter_moves()
        return random.choice(list(possible_moves))
