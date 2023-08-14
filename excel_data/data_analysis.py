import os
from dataclasses import dataclass
from typing import Optional, Union
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # fix matplotlib error with loop
from matplotlib import pyplot as plt, ticker as mtick


# path to folder with plots
PATH_TO_PLOTS = './static/plots'

# path to folder with Excel files
PATH_TO_EXCEL_FILES = './excel_data/files'

# category's
category = ('markets', 'markets_group', 'cm', 'kas', 'mr')

# columns and rows for plots
markets_columns = ('Visits', 'PSS', 'Osa', 'Ттask')

markets_rows = ('Auchan', 'Dixy', 'Lenta HM', 'Lenta SM', 'Magnit HM',
                'Magnit MK', 'Magnit MM', 'Metro', 'Okey', 'Perekrestok ',
                'Pyaterochka', 'Верный', 'Гиперглобус', 'Магнолия', 'Ярче')

markets_group_rows = ('Гипермаркеты', 'Магазины у дома', 'Супермаркеты')

cm_columns = ('% coverage', '% visits', 'PSS %', ' OSA %')

kas_mr_columns = ('% coverage', '% visits', 'PSS %', 'ср OSA %',
                  '% tactical task')

# dataclass to current Excel file name
@dataclass
class Filename:
    current = ''


current_file_name = Filename()


# create dirs for plot pictures
def create_dirs() -> None:
    for i in category:
        if not os.path.exists(f'{PATH_TO_PLOTS}/{i}'):
            os.makedirs(f'{PATH_TO_PLOTS}/{i}')


# change background color in table
def color_total_columns(value: int) -> Optional[str]:
    if value >= 1.05:
        return 'background-color: Lime; font-weight:bold'
    elif 1 <= value < 1.05:
        return 'background-color: Green; font-weight:bold'
    elif 0.95 <= value < 1:
        return 'background-color: Maroon; font-weight:bold'
    elif 0.90 <= value < 0.95:
        return 'background-color: Brown; font-weight:bold'
    elif value <= 0.90:
        return 'background-color: Red; font-weight:bold'
    return None


# open Excel file and return dataframe
def open_excel_file(file_name: str, sheet_name: str) -> pd.DataFrame:
    excel_file = pd.ExcelFile(f'{PATH_TO_EXCEL_FILES}/{file_name}')
    return pd.read_excel(excel_file, sheet_name)


# get plot in png
def get_plot(file_name: str, sheet_name: str, column_replace: str, sheet: str,
             index_name: str, output_file_name: str,
             rows: Optional[Union[str, tuple]], columns: tuple, left: float,
             rows_list: bool) -> None:
    df = open_excel_file(file_name, sheet_name)
    df.rename(columns={column_replace: sheet_name},
              inplace=True)
    df.set_index(sheet_name, inplace=True)
    if rows_list:
        df = df.loc[rows, columns]
    else:
        df = df.loc[df.index.values, columns]
    plt.figure()
    ax = df.plot(y=index_name,
                 kind='barh',
                 title=index_name,
                 legend=False,
                 xlim=(0.5, 1.3),
                 color='blue')
    ax.axvline(1,
               color='red',
               linestyle='--')
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    ax.bar_label(ax.containers[0],
                 fmt=lambda x: '{:.2f}%'.format(x * 100))
    plt.subplots_adjust(left=left)
    plt.gca().invert_yaxis()
    fig = ax.get_figure()
    fig.savefig(f'{PATH_TO_PLOTS}/{sheet}/{output_file_name}.png')
    plt.close('all')


# get table for markets in html format
def get_table_for_markets(file_name: str, sheet_name: str) -> str:
    df = open_excel_file(file_name, sheet_name)
    df.rename(columns={'Названия строк': sheet_name},
              inplace=True)
    df.set_index(sheet_name,
                 inplace=True)
    df = df.loc[markets_rows, markets_columns]
    df_styled = df.style.applymap(color_total_columns,
                                  subset=markets_columns)
    df_styled \
        .format('{:,.2%}'.format, subset=markets_columns) \
        .set_properties(**{'border': '1px solid black; font-size:100%'})
    table_markets = df_styled.to_html(justify="center")
    return table_markets


# get list of MR's for html selection
def get_mr_list(file_name: str, sheet_name: str) -> list:
    df = open_excel_file(file_name, sheet_name)
    df.set_index('МЕ', inplace=True)
    return sorted(list(df.index.values))


# get plots for all columns
def get_plots(file_name: str, sheet_name: str, column_replace: str, sheet: str,
              rows: Optional[Union[str, tuple]], columns: tuple, left: float,
              rows_list: bool) -> None:
    for i in columns:
        get_plot(file_name=file_name,
                 sheet_name=sheet_name,
                 column_replace=column_replace,
                 sheet=sheet,
                 index_name=i,
                 output_file_name=i,
                 rows=rows,
                 columns=columns,
                 left=left,
                 rows_list=rows_list)


# get all plots
def get_all_plots(file_name: str) -> None:
    get_plots(file_name=file_name,
              sheet_name='Сети',
              column_replace='Названия строк',
              sheet='markets',
              rows=markets_rows,
              columns=markets_columns,
              left=0.3,
              rows_list=True)
    get_plots(file_name=file_name,
              sheet_name='Группы',
              column_replace='Названия строк',
              sheet='markets_group',
              rows=markets_group_rows,
              columns=markets_columns,
              left=0.3,
              rows_list=True)
    get_plots(file_name=file_name,
              sheet_name='Сити',
              column_replace='Названия строк',
              sheet='cm',
              rows=None,
              columns=cm_columns,
              left=0.3,
              rows_list=False)
    get_plots(file_name=file_name,
              sheet_name='KAS',
              column_replace='КАС',
              sheet='kas',
              rows=None,
              columns=kas_mr_columns,
              left=0.5,
              rows_list=False)
    current_file_name.current = file_name


# get plot for specific MR
def get_mr_plots(file_name: str, mr_value: str) -> None:
    return get_plot(file_name=file_name,
                    sheet_name='MR',
                    column_replace='МЕ',
                    sheet='mr',
                    index_name=mr_value,
                    output_file_name='image',
                    rows=mr_value,
                    columns=kas_mr_columns,
                    left=0.2,
                    rows_list=True)


# get html code of plot pictures
def get_images_for_html(page: str) -> str:
    filenames = [f for f in os.listdir(f'{PATH_TO_PLOTS}/{page}')
                 if os.path.isfile(os.path.join(f'{PATH_TO_PLOTS}/{page}', f))]
    img_html_code = ''
    for i in filenames:
        img_html_code += (f'<img src = "{PATH_TO_PLOTS}/{page}/{i}" alt = '
              f'{i.replace(".png", "")} class="img-fluid">')
    return img_html_code


# get list of uploaded files
def get_files_list() -> list:
    return [f for f in os.listdir(PATH_TO_EXCEL_FILES) if
            os.path.isfile(os.path.join(PATH_TO_EXCEL_FILES, f))]


# get name of current file using for statistics
def get_current_file_name() -> str:
    return current_file_name.current
