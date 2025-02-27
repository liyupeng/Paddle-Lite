# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
sys.path.append('..')

from program_config import TensorConfig, ProgramConfig, OpConfig, CxxConfig, TargetType, PrecisionType, DataLayoutType, Place
import numpy as np
from functools import partial
from typing import Optional, List, Callable, Dict, Any, Set
import unittest
import hypothesis
import hypothesis.strategies as st


def sample_program_configs(draw):
    input_data_x_shape = draw(
        st.lists(
            st.integers(
                min_value=1, max_value=8), min_size=1, max_size=8))
    x_dims_size = len(input_data_x_shape)
    flatten = draw(st.booleans())
    axis = draw(st.integers(min_value=-x_dims_size, max_value=x_dims_size - 1))
    if flatten:
        axis = -1
    exclusive = draw(st.booleans())
    reverse = draw(st.booleans())

    cumsum_op = OpConfig(
        type="cumsum",
        inputs={"X": ["input_data_x"]},
        outputs={"Out": ["output_data"]},
        attrs={
            "axis": axis,
            "flatten": flatten,
            "exclusive": exclusive,
            "reverse": reverse
        })
    program_config = ProgramConfig(
        ops=[cumsum_op],
        weights={},
        inputs={"input_data_x": TensorConfig(shape=input_data_x_shape), },
        outputs=["output_data"])
    return program_config
