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
from hypothesis import assume


def sample_program_configs(draw):
    # inputs
    input_data_x_shape = draw(
        st.lists(
            st.integers(
                min_value=1, max_value=8), min_size=4, max_size=4))
    input_data_image_shape = draw(
        st.lists(
            st.integers(
                min_value=1, max_value=8), min_size=4, max_size=4))
    assume(input_data_x_shape[2] < input_data_image_shape[2])
    assume(input_data_x_shape[3] < input_data_image_shape[3])

    # attrs
    variances = draw(
        st.lists(
            st.floats(
                min_value=0.1, max_value=1.0), min_size=4, max_size=4))
    clip = draw(st.booleans())
    flatten_to_2d = draw(st.booleans())
    step_w = draw(st.floats(min_value=0.1, max_value=1.0))
    step_h = draw(st.floats(min_value=0.1, max_value=1.0))
    offset = draw(st.floats(min_value=0.1, max_value=1.0))
    fixed_sizes = draw(
        st.lists(
            st.floats(
                min_value=0.1, max_value=128.0), min_size=1, max_size=5))
    fixed_ratios = draw(
        st.lists(
            st.floats(
                min_value=0.1, max_value=5.0), min_size=1, max_size=5))
    densities = draw(
        st.lists(
            st.integers(
                min_value=1, max_value=10), min_size=1, max_size=5))

    density_prior_box_op = OpConfig(
        type="density_prior_box",
        inputs={"Input": ["input_data_x"],
                "Image": ["input_data_image"]},
        outputs={
            "Boxes": ["output_data_boxes"],
            "Variances": ["output_data_variances"]
        },
        attrs={
            "variances": variances,
            "clip": clip,
            "flatten_to_2d": flatten_to_2d,
            "step_w": step_w,
            "step_h": step_h,
            "offset": offset,
            "fixed_sizes": fixed_sizes,
            "fixed_ratios": fixed_ratios,
            "densities": densities
        })
    program_config = ProgramConfig(
        ops=[density_prior_box_op],
        weights={},
        inputs={
            "input_data_x": TensorConfig(shape=input_data_x_shape),
            "input_data_image": TensorConfig(shape=input_data_image_shape)
        },
        outputs=["output_data_boxes", "output_data_variances"])
    return program_config
