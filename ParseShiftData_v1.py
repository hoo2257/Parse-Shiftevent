import pandas as pd
import os


def get_group_idx(signals, mdf):
    """
    추출 할 CAN IDs 의 그룹  인덱스 값 반환하는 매서드
    :param signals: 추출 CAN IDs
    :param mdf: mdf 오브젝트
    :return: 추출 CAN IDs group #
    """
    signal_loc = {}
    for signal in signals:
        loc = mdf.whereis(signal)
        signal_loc[signal] = loc[0]

    return signal_loc


def get_tm_disc(input_mdf_, tm_disc_signals_):
    # df_shift = pd.DataFrame()
    df_shift_sta = pd.DataFrame()
    df_cls = pd.DataFrame()
    tm_disc_sig_loc = get_group_idx(tm_disc_signals_, input_mdf_)


    for signal in tm_disc_signals_:
        group_idx = tm_disc_sig_loc[signal]
        group = tm_disc_sig_loc[signal][0]
        index = tm_disc_sig_loc[signal][1]

        temp = input_mdf_.get_group(group_idx[0])

        for col_name in temp.columns:
            name = col_name.split("\\")[0]
            if signal.lower() == name.lower():
                if not "LHTCU".lower() in name.lower():
                    df_shift_sta = pd.concat([df_shift_sta, temp[col_name]], axis=1)
                    timestamp_df_shift_sta = input_mdf_.get(group=group, index=index).timestamps # 진짜 Timestamp 가져옴!!
                    df_shift_sta["timestamp"] = timestamp_df_shift_sta
                else:
                    df_cls = pd.concat([df_cls, temp[col_name]], axis=1)
                    timestamp_cls = input_mdf_.get(group=group, index=index).timestamps
                    df_cls["timestamp"] = timestamp_cls

    df_shift_sta = df_shift_sta.set_index("timestamp")
    df_cls = df_cls.set_index("timestamp")
    df_shift = pd.concat([df_shift_sta, df_cls], axis=1)
    df_shift.fillna(method="ffill", inplace=True)

    return df_shift


def get_12up_time(input_mdf_, tm_disc_sig):
    tm_state = get_tm_disc(input_mdf_, tm_disc_sig)
    tm_state["timestamp"] = tm_state.index
    shift_flag = 0
    times = []
    shift_time = []

    for i, data in enumerate(tm_state.values):

        if data[0] == b'1st speed' and data[1] == b'2nd speed' and data[2] == b'PON UP' and shift_flag == 0:
            #             print("SHIFT START")
            #             print(data)
            shift_time.append(data[-1])
            shift_flag = 1

        elif data[0] == b'2nd speed' and data[1] == b'2nd speed' and data[2] == b'NO SHIFT' and shift_flag == 1:
            shift_time.append(data[-1])
            shift_flag = 0
            #             print(data)
            #             print("SHIFT DONE")
            times.append(shift_time)
            shift_time = []

    return times


def get_tm_cont(input_mdf, tm_cont_signals):
    cont_df = pd.DataFrame()

    for sig in tm_cont_signals:
        sig_loc = input_mdf.whereis(sig)

        if len(sig_loc) != 0:
            group = sig_loc[0][0]
            index = sig_loc[0][1]
            timestamp = input_mdf.get(group=group, index=index).timestamps
            temp_df = input_mdf.get_group(group)
            temp_df.index = timestamp
            for col_name in temp_df.columns:
                name = col_name.split("\\")[0]

                if name == sig:
                    cont_df = pd.concat([cont_df, temp_df[col_name]], axis=1)
        else:
            print("[WARNING] Missing Signal : ", sig)
            pass

    cont_df = cont_df.interpolate()
    cont_df = cont_df.fillna(0)

    return cont_df


def ParseShiftData(input_mdf, tm_disc_signals, tm_cont_signals, file_name):
    save_dir = "Sorted/{}".format(file_name)
    # tm_disc_sig_loc = get_group_idx(tm_disc_signals, input_mdf)
    shift_time = get_12up_time(input_mdf, tm_disc_signals)

    if len(shift_time) != 0:
        cont_df = get_tm_cont(input_mdf, tm_cont_signals)

        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        else:
            pass

        for i, time in enumerate(shift_time):
            df_ = cont_df.loc[(cont_df.index >= time[0]) & (cont_df.index <= time[1])]

            df_.to_pickle("{}/{}.pkl".format(save_dir, i))
        #         df_.to_csv("{}/{}.csv".format(file_name,i))
        print("[INFO] Found {} Events of 1-2 Upshift Data! Saving to...".format(len(shift_time)), save_dir)