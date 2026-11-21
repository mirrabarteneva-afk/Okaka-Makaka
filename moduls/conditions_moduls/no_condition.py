import pandas as pd
from typing import Any, List, Optional, Union


def no_conditions(oper: str,
                  cond: None,
                  df: pd.DataFrame,
                  column: str,
                  found: Union[str, List[str]]
                  ):
    try:
        if oper == '=':
            data_lst = df[found].loc[df[column] == cond, found].values.tolist()
        
        if oper == '>':
            data_lst = df[found].loc[df[column] > cond, found].values.tolist()
        
        if oper == '<':
            data_lst = df[found].loc[df[column] < cond, found].values.tolist()

        if oper == '>=':
            data_lst = df[found].loc[df[column] >= cond, found].values.tolist()

        if oper == '<=':
            data_lst = df[found].loc[df[column] <= cond, found].values.tolist()

        if oper == 'Диапазон вкл':
            cond_st = str(cond).strip()

            for sep in (';', ':', ', '):
                if sep in cond_st:
                    res = cond_st.split(sep)
                    break

                else:
                    res = cond_st.split()

            x, x1 = res
            mask = df[column].between(float(x), float(x1), inclusive='both')
            data_lst = df.loc[mask, found].values.tolist()

        if oper == 'Диапазон не вкл':
            cond_st = str(cond).strip()

            for sep in (';', ':', ', '):
                if sep in cond_st:
                    res = cond_st.split(sep)
                    break

                else:
                    res = cond_st.split()

            x, x1 = res
            mask = df[column].between(float(x), float(x1), 'neither')
            data_lst = df.loc[mask, found].values.tolist()


        if oper == 'В тексте':
            mask = df[column].str.contains(cond, case=False, na=False)
            data_lst = df.loc[mask, found].values.tolist()

    except Exception:
        return
    
    if oper == 'Пусто':
        mask = df[column].isna() | (df[column].astype(str).str.strip() == '')
        data_lst = df.loc[mask, found].values.tolist()

    if oper == 'Не пусто':
        mask = df[column].notna() & (df[column].astype(str).str.strip() != '')
        data_lst = df.loc[mask, found].values.tolist()

    return data_lst