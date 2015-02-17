
DEFAULT_AI_NAME = "simple_combo"

from puyo.board import Board
from puyo.beanfinder import BeanFinder
from puyo.gccontrol import GamecubeController
from puyo.vision import Vision
from puyo.driver import Driver
from puyo import ai

AI_REGISTRY = {
    'simple_combo': ai.SimpleComboAI,
    'random': ai.RandomAI,
    'simple_greedy': ai.SimpleGreedyAI,
}

DEFAULT_AI = AI_REGISTRY[DEFAULT_AI_NAME]
