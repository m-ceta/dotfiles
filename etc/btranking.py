import sys
import os
import os.path
import numpy as np
import matplotlib.pyplot as plt
import json

dir_home = os.environ['HOME']
dir_ptr = os.path.join(dir_home, "ptranking")
data_id = "BTR2021"
num_features = 188
sys.path.append(dir_ptr)
import ptranking.data.data_utils
# ===============================================================
def my_get_data_meta(data_id=None):
    data_meta = dict(num_features=num_features, has_comment=False, 
                     label_type=ptranking.data.data_utils.LABEL_TYPE.MultiLabel, 
                     max_rele_level=5, fold_num=5)
    return data_meta
setattr(ptranking.data.data_utils, "get_data_meta", my_get_data_meta)
ptranking.data.data_utils.MSLETOR.append(data_id)
# ===============================================================

from ptranking.ltr_adhoc.eval.ltr import LTREvaluator
# ===============================================================
def my_grid_run(self, model_id, dir_json, vali_k, cutoffs, debug=False):
    if dir_json is None:
        return
    data_eval_sf_json = dir_json + 'Data_Eval_ScoringFunction.json'
    self.set_eval_setting(debug=debug, eval_json=data_eval_sf_json)
    self.set_data_setting(data_json=data_eval_sf_json)
    self.set_scoring_function_setting(sf_json=data_eval_sf_json)
    self.set_model_setting(model_id=model_id, dir_json=dir_json)
    self.declare_global(model_id=model_id)
    max_cv_avg_scores = np.zeros(len(cutoffs))  # fold average
    k_index = cutoffs.index(vali_k)
    max_common_para_dict, max_sf_para_dict, max_model_para_dict = None, None, None

    for data_dict in self.iterate_data_setting():
        for eval_dict in self.iterate_eval_setting():
            assert self.eval_setting.check_consistence(vali_k=vali_k, cutoffs=cutoffs) # a necessary consistence

            for sf_para_dict in self.iterate_scoring_function_setting(data_dict=data_dict):
                for model_para_dict in self.iterate_model_setting():
                    curr_cv_avg_scores = self.kfold_cv_eval(data_dict=data_dict, eval_dict=eval_dict,
                                                        sf_para_dict=sf_para_dict, model_para_dict=model_para_dict)
                    if curr_cv_avg_scores[k_index] > max_cv_avg_scores[k_index]:
                        max_cv_avg_scores, max_sf_para_dict, max_eval_dict, max_model_para_dict = \
                                                       curr_cv_avg_scores, sf_para_dict, eval_dict, model_para_dict

    # log max setting
    self.log_max(data_dict=data_dict, eval_dict=max_eval_dict,
                 max_cv_avg_scores=max_cv_avg_scores, sf_para_dict=max_sf_para_dict,
                 log_para_str=self.model_parameter.to_para_string(log=True, given_para_dict=max_model_para_dict))
setattr(LTREvaluator, "grid_run2", my_grid_run)
# ===============================================================

def update_json_settings(dir_json, dir_rdata, dir_out, vali_k, cutoffs):
    data_eva_sf_file = "Data_Eval_ScoringFunction.json"
    data_eva_sf_settings = {
      "DataSetting": {
        "data_id":data_id,
        "dir_data":dir_rdata,
        "min_docs":[4],
        "min_rele":[0],
        "train_batch_size":[1],
        "num_features":num_features,
        "has_comment":[False],
        "fold_num":[5],
        "scale_data":[True],
        "scaler_id":None,
        "binary_rele":[False],
        "unknown_as_zero":[False],
        "train_presort":[True]
      },
      "EvalSetting": {
        "dir_output":dir_out,
        "epochs":100,
        "do_validation":True,
        "vali_k":vali_k,
        "cutoffs":cutoffs,
        "loss_guided":False,
        "do_log":True,
        "log_step":2,
        "do_summary":True,
        "mask":{
          "mask_label":False,
          "mask_type":["rand_mask_all"],
          "mask_ratio":[0.2]
        }
      },
      "SFParameter": {
        "BN":[False],
        "RD":[False],
        "layers":[5],
        "apply_tl_af":[True],
        "hd_hn_tl_af":["R", "GE"]
      }
    }
    RankNet_file = "RankNetParameter.json"
    RankNet_settings = {
      "sigma":[1.0]
    }
    LambdaRank_file = "LambdaRankParameter.json"
    LambdaRank_settings = {
      "sigma":[1.0]
    }
    WassRank_file = "WassRankParameter.json"
    WassRank_settings = {
      "mode":["WassLossSta"],
      "itr":[10],
      "lam":[0.1],
      "cost_type":["eg"],
      "non_rele_gap":[10],
      "var_penalty":[2.71828],
      "group_base":[4],
      "smooth":["ST"],
      "norm":["BothST"]
    }
    LambdaLoss_file = "LambdaLossParameter.json"
    LambdaLoss_settings = {
      "k":[5],
      "mu":[5.0],
      "sigma":[1.0],
      "loss_type":["NDCG_Loss2"]
    }
    json_list = [
        [data_eva_sf_file, data_eva_sf_settings],
        [RankNet_file, RankNet_settings],
        [LambdaRank_file, LambdaRank_settings],
        [WassRank_file, WassRank_settings],
        [LambdaLoss_file, LambdaLoss_settings],
    ]
    for file_name, settings in json_list:
        file_path = os.path.join(dir_json, file_name)
        with open(file_path, 'w') as f:
            json.dump(settings, f, ensure_ascii=False)

def create_ltr_evaluator(dir_json, dir_rdata, dir_out, vali_k, cutoffs):
    update_json_settings(dir_json, dir_rdata, dir_out, vali_k, cutoffs)
    evaluator = LTREvaluator()
    return evaluator

def start_train(models_to_run, dir_json, dir_rdata, dir_out, vali_k, cutoffs, debug):
    evaluator = create_ltr_evaluator(dir_json, dir_rdata, dir_out, vali_k, cutoffs)
    for model_id in models_to_run:
        evaluator.grid_run2(model_id, dir_json, vali_k, cutoffs, debug)

def predict(model_id, model_save_path, data_file_path, dir_json, dir_rdata, dir_out, vali_k, cutoffs, debug):
    evaluator = create_ltr_evaluator(dir_json, dir_rdata, dir_out, vali_k, cutoffs)

    data_eval_sf_json = os.path.join(dir_json, "Data_Eval_ScoringFunction.json")
    evaluator.set_eval_setting(debug=debug, eval_json=data_eval_sf_json)
    evaluator.set_data_setting(data_json=data_eval_sf_json)
    evaluator.set_scoring_function_setting(sf_json=data_eval_sf_json)
    evaluator.set_model_setting(model_id=model_id, dir_json=dir_json)
    evaluator.declare_global(model_id=model_id)

    model_para_dict = evaluator.get_default_model_setting()
    sf_para_dict = evaluator.get_default_scoring_function_setting()

    data = LTRDataset(file=data_file_path, data_dict=data_dict, eval_dict=eval_dict)
    ranker = evaluator.load_ranker(sf_para_dict, model_para_dict)
    ranker.load(model_save_path)
    return ranker.predict(data[0][1])

