import pypeline as pype
from pypeline import pipeline_img_series

import sys
import os

import time

img_filepath=r'\\skynet\PechinTest2\emphysema_pipeline_test_20170124\library\recon\100\5a1eebd46534e0e22036254ddd54c4db_k1_st2.0\img\5a1eebd46534e0e22036254ddd54c4db_d100_k1_st2.0.img'
prm_filepath=r'\\skynet\PechinTest2\emphysema_pipeline_test_20170124\library\recon\100\5a1eebd46534e0e22036254ddd54c4db_k1_st2.0\img\5a1eebd46534e0e22036254ddd54c4db_d100_k1_st2.0.prm'

test=pipeline_img_series(img_filepath,prm_filepath)

test.to_hr2(r'\\skynet\PechinTest2\emphysema_pipeline_test_20170124\library\recon\100\5a1eebd46534e0e22036254ddd54c4db_k1_st2.0\img\test.hr2')
