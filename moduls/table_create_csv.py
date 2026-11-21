import pandas as pd
from pathlib import Path
from moduls.conditions_moduls.condition_and import filters_cond_and
from moduls.conditions_moduls.condition_or import filters_cond_or
from moduls.conditions_moduls.no_condition import no_conditions

def csv_table_create(columns: list, path: Path, delim: str, conditions=None) -> tuple:
    try:
        df = pd.read_csv(path, delimiter=delim, encoding='utf-8')
    except FileNotFoundError:
        return (columns, [])
    

    found = [col for col in columns if col in df.columns]
    headers = found
    data_lst = df[found].values.tolist()

    if conditions:
        if len(conditions) > 1:
            for i in range(len(conditions)):
                if conditions[i] == 'AND' or conditions[i] == 'OR':
                    column = conditions[i - 1][0]
                    column2 = conditions[i + 1][0]

                    if column == 'Нет' or column2 == 'Нет':
                        return (headers, data_lst)
                    
                    oper = conditions[i - 1][1]
                    oper2 = conditions[i + 1][1]

                    try:
                        cond = float(conditions[i - 1][2])
                        cond2 = float(conditions[i + 1][2])
                    except ValueError:
                        cond = conditions[i - 1][2]
                        cond2 = conditions[i + 1][2]

                        print(cond2)
                        print(type(cond2))

                    try:
                        if conditions[i] == 'AND':
                            data_lst = filters_cond_and(oper, cond, df, column, found, oper2, column2, cond2)

                        if conditions[i] == 'OR':
                            data_lst = filters_cond_or(oper, cond, df, column, found, oper2, column2, cond2)

                    except TypeError:
                        return 'Несовпадение типов!'

        else:
            column = conditions[0][0]
            oper = conditions[0][1]

            try:
                cond = float(conditions[0][2])

            except ValueError:
                cond = conditions[0][2]

            try:
                data_lst = no_conditions(oper, cond, df, column, found)
                
            except TypeError:
                return (headers, [])

    return (headers, data_lst)