#!/usr/bin/env python
# Example invocation:
# ./build_move_example_datasets.py some_sgf_games.zip train.npz test.npz

import h5py
import numpy as np
import random
import sys
import util


def build_move_example_datasets(sgfzip_input, h5_output_file):
  """Turns a zip file of SGFs into a training and testing set full of move
  examples.  Passing moves are ignored.  Train/test split is by game
  to better detect potential per-game overfit.  About 1/10 games end up in
  the test set."""

  examples = []
  game_number = 0
  for game in util.zip_to_sgf_contents(sgfzip_input):
    game_number += 1
    if game_number % 100 == 0:
      print "Processing game %d." % game_number
    examples.extend(list(util.game_to_move_examples(game)))
  print "Done reading games.  Saving."
  util.save_labelled_examples(examples, h5_output_file)


if __name__ == '__main__':
  build_move_example_datasets(sys.argv[1], sys.argv[2])
