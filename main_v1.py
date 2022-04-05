from ParseShiftData_v1 import *
import glob
from asammdf import MDF
import os


mdfs = glob.glob("MDFs/*")

APS = "HEV_AccelPdlVal"
eng_rpm = "HEV_EngSpdVal"
BPS = "IEB_StrkDpthPcVal"
tr_class = "LHTCU_ShftTrgtClsSta"
cur_gear = "HTCU_CurrGearSta"
target_gear = "HTCU_TrgtGearSta"
wheel_spd = "WHL_SpdFLVal"
accel = "YRS_LongAccelVal"
mot_spd = "NTU"  # tm_in_spd 와 같음
tm_out_spd = "NAB"
tm_delta_acc = "ntug_SyncFilt"
shift_phase = "esa_Phase"

tm_disc_signals = (cur_gear, target_gear, tr_class)
tm_cont_signals = (APS, eng_rpm, BPS, wheel_spd, mot_spd, tm_out_spd, tm_delta_acc)
# tm_cont_signals = (APS, eng_rpm, BPS, wheel_spd, mot_spd, tm_out_spd)


for mdf in mdfs:

    file_name_, file_extension = os.path.splitext(mdf)

    try:
        if file_extension == ".dat" or file_extension == ".mf4":
            input_mdf = MDF(mdf)
            file_name = file_name_.split("\\")[-1]
            ParseShiftData(input_mdf, tm_disc_signals, tm_cont_signals, file_name)
        else:
            pass
    except Exception as e:
        print(e)





