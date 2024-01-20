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
