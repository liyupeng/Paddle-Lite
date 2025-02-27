// Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once
#include <string>
#include <vector>
#include "lite/core/op_lite.h"
#include "lite/core/scope.h"
#include "lite/utils/all.h"

namespace paddle {
namespace lite {
namespace operators {

class ReshapeOp : public OpLite {
 public:
  ReshapeOp() {}
  explicit ReshapeOp(const std::string &op_type) : OpLite(op_type) {}

  bool CheckShape() const override;

  bool InferShapeImpl() const override;

  bool InferShapeWithCache() const override { return true; }

  bool AttachImpl(const cpp::OpDesc &opdesc, lite::Scope *scope) override;

  void AttachKernel(KernelBase *kernel) override { kernel->SetParam(param_); }
  std::string DebugString() const override { return "reshape"; }

  bool InferType() override {
    param_.output->set_precision(param_.x->precision());
    return true;
  }

#ifdef LITE_WITH_PROFILE
  void GetOpRuntimeInfo(paddle::lite::profile::OpCharacter *ch) {
    auto input_dims = param_.x->dims();
    auto output_dims = param_.output->dims();
    ch->input_shape = ch->DimToStr(input_dims);
    ch->output_shape = ch->DimToStr(output_dims);
  }
#endif

 protected:
  mutable ReshapeParam param_;
};

class Reshape2Op : public ReshapeOp {
 public:
  Reshape2Op() : ReshapeOp() {}
  explicit Reshape2Op(const std::string &op_type) : ReshapeOp(op_type) {}

  bool CheckShape() const override;

  bool InferShapeImpl() const override;

  bool InferShapeWithCache() const override { return true; }

  bool AttachImpl(const cpp::OpDesc &opdesc, lite::Scope *scope) override;

  void AttachKernel(KernelBase *kernel) override { kernel->SetParam(param_); }
  std::string DebugString() const override { return "reshape2"; }

  bool InferType() override {
    param_.output->set_precision(param_.x->precision());
    return true;
  }
};

std::vector<DDim::value_type> ValidateShape(const std::vector<int> &shape,
                                            const DDim &input_dims);

}  // namespace operators
}  // namespace lite
}  // namespace paddle
