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

from auto_scan_base import AutoScanBaseTest
import numpy as np
import logging
import abc
import enum
import unittest
import paddle
import copy
from typing import Optional, List, Callable, Dict, Any, Set
from paddlelite.lite import *


def ParsePlaceInfo(place_str):
    # todo: this func should be completed later
    infos = ''.join(place_str.split()).split(",")
    if len(infos) == 1:
        if infos[0] in TargetType.__members__:
            return Place(eval("TargetType." + infos[0]))
        else:
            logging.fatal("Error place info: " + place_str)
    elif len(infos) == 2:
        if (infos[0] in TargetType.__members__) and (
                infos[1] in PrecisionType.__members__):
            return Place(
                eval("TargetType." + infos[0]),
                eval("PrecisionType." + infos[1]))
        else:
            logging.fatal("Error place info: " + place_str)
    elif len(infos) == 3:
        if (infos[0] in TargetType.__members__) and (
                infos[1] in PrecisionType.__members__) and (
                    infos[2] in DataLayoutType.__members__):
            return Place(
                eval("TargetType." + infos[0]),
                eval("PrecisionType." + infos[1]),
                eval("DataLayoutType." + infos[2]))
        else:
            logging.fatal("Error place info: " + place_str)
    else:
        logging.fatal("Error place info: " + place_str)


def ParsePaddleLiteConfig(self, config):
    lite_config = CxxConfig()
    if "valid_targets" in config:
        valid_places = []
        for place_str in config["valid_targets"]:
            valid_places.append(ParsePlaceInfo(place_str))
        lite_config.set_valid_places(valid_places)
    if "thread" in config:
        lite_config.set_threads(config["thread"])
    return lite_config


class AutoScanTest(AutoScanBaseTest):
    def run_lite_config(self, model, params, inputs,
                        pred_config) -> Dict[str, np.ndarray]:
        # 1. store original model
        with open(self.cache_dir + "/model", "wb") as f:
            f.write(model)
        with open(self.cache_dir + "/params", "wb") as f:
            f.write(params)

        # 2. run inference
        config = ParsePaddleLiteConfig(self, pred_config)
        config.set_model_buffer(model, len(model), params, len(params))
        predictor = create_paddle_predictor(config)

        for name in inputs:
            input_tensor = predictor.get_input_by_name(name)
            input_tensor.from_numpy(inputs[name]['data'])
            if inputs[name]['lod'] is not None:
                input_tensor.set_lod(inputs[name]['lod'])
        predictor.run()

        # 3. inference results
        result = {}
        for out_name in predictor.get_output_names():
            result[out_name] = predictor.get_output_by_name(out_name).numpy()
        result_res = copy.deepcopy(result)

        # 4. optimized model
        predictor.save_optimized_pb_model(self.cache_dir + "/opt_model/")
        with open(self.cache_dir + "/opt_model/model", "rb") as f:
            model = f.read()

        return result_res, model


class FusePassAutoScanTest(AutoScanTest):
    def run_and_statis(self,
                       quant=False,
                       max_examples=100,
                       reproduce=None,
                       min_success_num=25,
                       max_duration=180,
                       passes=None):
        assert passes is not None, "Parameter of passes must be defined in function run_and_statis."
        super().run_and_statis(quant, max_examples, reproduce, min_success_num,
                               max_duration, passes)
