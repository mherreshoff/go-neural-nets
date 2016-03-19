#!/usr/bin/env python
# Example invocation:
# ./build_move_example_datasets.py some_sgf_games.zip train.npz test.npz

import sys
import random
import numpy as np
import util

def save_labelled_examples(examples, file_name):
  # For now, throw out passes:
  examples = [e for e in examples if e[1] is not None]

  boards = np.array(example[0] for example in examples)
  labels = np.array(example[1] for example in examples)
  np.savez(file_name, boards=boards, labels=labels)


def build_move_example_datasets(sgfzip_input, train_output, test_output):
  train = []
  test = []
  for game in util.zip_to_sgf_contents(sgfzip_input):
    examples = list(util.game_to_move_examples(game))
    if random.randint(0, 10) == 0:
      test.extend(examples)
    else:
      train.extend(examples)
  save_labelled_examples(random.shuffle(train), train_output)
  save_labelled_examples(random.shuffle(test), test_output)

if __name__ == '__main__':
  build_move_example_datasets(sys.argv[1], sys.argv[2], sys.argv[3])
