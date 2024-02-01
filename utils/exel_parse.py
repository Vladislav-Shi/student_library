import pandas as pd


def get_raw_disciplines(fp) -> list:
    """Получает список дисциплин
    ключ -- номер курса. Значение -- список предметов
     """
    df = pd.read_excel(fp, sheet_name='Практическая  подготовка')
    new_keys = df.iloc[0].map(lambda x: str(x).strip())
    df = df.shift(-1)
    df.columns = new_keys
    df = df[['Наименование', 'Семестр/ Курс']]
    df = df.dropna().reset_index(drop=True)
    return df.to_dict(orient='records')


def get_raw_disciplines_plan(fp) -> list:
    """Тоже самое как выше, но по листу ПланСвод"""
    df = pd.read_excel(fp, sheet_name='ПланСвод')
    new_keys = df.iloc[1].map(lambda x: str(x).strip())
    df = df.shift(-2)
    df.columns = new_keys
    df = df.iloc[:, ~df.columns.duplicated()]

    df = df.dropna(subset=['Наименование']).reset_index(drop=True)

    df = df[['Наименование', 'Экза мен', 'Зачет', 'Зачет с оц.']]
    df = df[~df['Наименование'].str.startswith('Дисциплины')]
    df['Семестр/ Курс'] = df['Экза мен'].fillna(df['Зачет']).fillna(df['Зачет с оц.'])
    df = df[['Наименование', 'Семестр/ Курс']]
    return df.to_dict(orient='records')






if __name__ == '__main__':
    x = get_raw_disciplines_plan(
        '/home/vladislav/PycharmProjects/student_library/xlsx/09_04_03_Prikladnaya_informatika_Informatsionnoe_obespechenie-2020.xlsx')
    print(x)
