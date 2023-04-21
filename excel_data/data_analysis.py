import matplotlib
matplotlib.use('Agg') # fix matplotlib error with loop
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


# path to folder with plots
path_to_plots = './static/plots/'

category = ['markets', 'markets_group', 'cm', 'kas', 'mr']

# columns and rows for plots
markets_columns = ['Visits', 'PSS', 'Osa', 'Ттask']

markets_rows = ['Auchan', 'Dixy', 'Lenta HM', 'Lenta SM', 'Magnit HM',
                'Magnit MK', 'Magnit MM', 'Metro', 'Okey', 'Perekrestok ',
                'Pyaterochka', 'Верный', 'Гиперглобус', 'Магнолия', 'Ярче']

markets_group_rows = ['Гипермаркеты', 'Магазины у дома', 'Супермаркеты']

cm_columns = ['% coverage', '% visits', 'PSS %', ' OSA %']

kas_mr_columns = ['% coverage', '% visits', 'PSS %', 'ср OSA %',
                  '% tactical task']


# create dirs for plot pictures
def create_dirs():
    for i in category:
        if not os.path.exists(f'./static/plots/{i}'):
            os.makedirs(f'./static/plots/{i}')


# change background color
def color_total_columns(value):
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


# open Excel file and return dataframe
def open_excel_file(file_name, sheet_name):
    excel_file = pd.ExcelFile(f'./excel_data/files/{file_name}')
    return pd.read_excel(excel_file, sheet_name)


# get plot in png
def get_plot(file_name, sheet_name, column_replace, sheet, index_name,
             output_file_name, rows, columns, left, rows_list):
    df = open_excel_file(file_name, sheet_name)
    df.rename(columns={column_replace: sheet_name},
              inplace=True)
    df.set_index(sheet_name, inplace=True)
    if rows_list:
        df = df.loc[rows, columns]
    else:
        df = df.loc[df.index.values, columns]
    ax = plt.figure()
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
    fig.savefig(f'./static/plots/{sheet}/{output_file_name}.png')
    plt.close('all')


# get table in html format
def get_table_for_markets(file_name, sheet_name):
    df = open_excel_file(file_name, sheet_name)
    df.rename(columns={'Названия строк': sheet_name},
              inplace=True)
    df.set_index(sheet_name,
                 inplace=True)
    df = df.loc[markets_rows, markets_columns]
    df_styled = df.style.applymap(color_total_columns,
                                  subset=markets_columns)
    df_styled\
        .format('{:,.2%}'.format, subset=markets_columns)\
        .set_properties(**{'border': '1px solid black; font-size:100%'})
    table_markets = df_styled.to_html(justify="center")
    return table_markets


# get list of MR's for html selection
def get_mr_list(file_name, sheet_name):
    df = open_excel_file(file_name, sheet_name)
    df.set_index('МЕ', inplace=True)
    return sorted(list(df.index.values))


# get plots for all columns
def get_plots(file_name, sheet_name, column_replace, sheet, rows, columns,
              left, rows_list):
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
def get_all_plots():
    get_plots(file_name='P04_Stats.xlsx',
              sheet_name='Сети',
              column_replace='Названия строк',
              sheet='markets',
              rows=markets_rows,
              columns=markets_columns,
              left=0.3,
              rows_list=True)
    get_plots(file_name='P04_Stats.xlsx',
              sheet_name='Группы',
              column_replace='Названия строк',
              sheet='markets_group',
              rows=markets_group_rows,
              columns=markets_columns,
              left=0.3,
              rows_list=True)
    get_plots(file_name='P04_Stats.xlsx',
              sheet_name='Сити',
              column_replace='Названия строк',
              sheet='cm',
              rows=None,
              columns=cm_columns,
              left=0.3,
              rows_list=False)
    get_plots(file_name='P04_Stats.xlsx',
              sheet_name='KAS',
              column_replace='КАС',
              sheet='kas',
              rows=None,
              columns=kas_mr_columns,
              left=0.5,
              rows_list=False)


# get plot for specific MR
def get_mr_plots(mr_value):
    return get_plot(file_name='P04_Stats.xlsx',
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
def get_images_for_html(page):
    filenames = [f for f in os.listdir(f'{path_to_plots}/{page}')
                 if os.path.isfile(os.path.join(f'{path_to_plots}/{page}', f))]
    x = ''
    for i in filenames:
        x += (f'<img src = "./static/plots/{page}/{i}" alt = '
              f'{i.replace(".png", "")} >')
    return x
