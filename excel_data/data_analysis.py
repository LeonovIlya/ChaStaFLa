import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# path to folder with plots
path_to_plots = './static/plots/'

category = ['markets', 'cm', 'kas', 'mr']

# markets columns and rows in markets_sheet
market_columns = ['Visits', 'PSS', 'Osa', 'Ттask']

markets_rows = ['Auchan', 'Dixy', 'Lenta HM', 'Lenta SM', 'Magnit HM',
                'Magnit MK', 'Magnit MM', 'Metro', 'Okey', 'Perekrestok ',
                'Pyaterochka', 'Верный', 'Гиперглобус', 'Магнолия', 'Ярче']

cm_columns = ['% coverage', '% visits', 'PSS %', ' OSA %']
cm_rows = ['Ушакова Наталья', 'Клабукова Виктория']


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
def get_plot(file_name, sheet_name, sheet, index_name, rows, columns):
    df = open_excel_file(file_name, sheet_name)
    df.rename(columns={'Названия строк': sheet_name},
              inplace=True)
    df.set_index(sheet_name, inplace=True)
    df = df.loc[rows, columns]
    ax = df.plot(y=index_name,
                 kind='barh',
                 title=index_name,
                 legend=False,
                 xlim=(0.6, 1.2),
                 color='blue')
    ax.axvline(1,
               color='red',
               linestyle='--')
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    ax.bar_label(ax.containers[0],
                 fmt=lambda x: '{:.2f}%'.format(x * 100))
    plt.subplots_adjust(left=0.3)
    fig = ax.get_figure()
    fig.savefig(f'./static/plots/{sheet}/{index_name}.png')


# get table in html format
def get_table_for_markets(file_name, sheet_name):
    df = open_excel_file(file_name, sheet_name)
    df.rename(columns={'Названия строк': sheet_name},
              inplace=True)
    df.set_index(sheet_name,
                 inplace=True)
    df = df.loc[markets_rows, market_columns]
    df_styled = df.style.applymap(color_total_columns,
                                  subset=market_columns)
    df_styled\
        .format('{:,.2%}'.format, subset=market_columns)\
        .set_properties(**{'border': '1px solid black; font-size:100%'})
    table_markets = df_styled.to_html(justify="center")
    return table_markets


# gen pngs for all total columns
def get_plots(filename, sheet_name, sheet, rows, columns):
    for i in columns:
        get_plot(file_name=filename,
                 sheet_name=sheet_name,
                 sheet=sheet,
                 rows=rows,
                 columns=columns,
                 index_name=i)


def get_all_plots():
    get_plots('P04_Stats.xlsx', 'Сети', 'markets', markets_rows,
              market_columns)
    get_plots('P04_Stats.xlsx', 'Сити', 'cm', cm_rows, cm_columns)


def get_images_for_html(page):
    filenames = [f for f in os.listdir(f'{path_to_plots}/{page}')
                 if os.path.isfile(os.path.join(f'{path_to_plots}/{page}', f))]
    x = ''
    for i in filenames:
        x += (f'<img src = "./static/plots/{page}/{i}" alt = '
              f'{i.replace(".png", "")} >')
    return x
