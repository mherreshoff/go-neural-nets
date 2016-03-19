#!/usr/bin/env python
# Example invocation:
# ./build_move_example_datasets.py some_sgf_games.zip train.npz test.npz

import sys
import random
import numpy as np
import util

def save_labelled_examples(examples, file_name):
  """Write the examples (minus moves where the player passes) to an npz
  file.  The file contains two arrays.  Boards Nx3x19x19 and labels (the
  moves) Nx2."""

  # For now, throw out passes:
  examples = [e for e in examples if e[1] is not None]

  boards = np.array(example[0] for example in examples)
  moves = np.array(example[1] for example in examples)
  np.savez(file_name, boards=boards, moves=moves)


def build_move_example_datasets(sgfzip_input, train_output, test_output):
  """Turns a zip file of SGFs into a training and testing set full of move
  examples.  Passing moves are ignored.  Train/test split is by game
  to better detect potential per-game overfit.  About 1/10 games end up in
  the test set."""

  train = []
  test = []
  game_number = 0
  for game in util.zip_to_sgf_contents(sgfzip_input):
    game_number += 1
    if game_number % 100 == 0:
      print "Processing game %d." % game_number
    examples = list(util.game_to_move_examples(game))
    if random.randint(0, 10) == 0:
      test.extend(examples)
    else:
      train.extend(examples)
  print "Done reading games.  Shuffling and saving."
  save_labelled_examples(random.shuffle(train), train_output)
  save_labelled_examples(random.shuffle(test), test_output)

if __name__ == '__main__':
  build_move_example_datasets(sys.argv[1], sys.argv[2], sys.argv[3])
