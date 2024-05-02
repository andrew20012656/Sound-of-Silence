import json
import plotly.express as px
from dash import Dash, dcc, html, dash_table, callback, Output, Input
from data_validator import *
from location_anonymizer import *
from pprint import pprint

if __name__ == "__main__":
    input_dir = sys.argv[1]
    participant = os.path.dirname(os.path.dirname(input_dir))
    print(participant)

    data_validator = DataValidator(input_dir)
    data_validator.load_history()

    # stats = load_basic_stats(input_file)
    stats = data_validator.stats
    pprint(stats)

    # Extract the basic_stats dictionary
    basic_stats_dict = stats['basic_stats']
    num_of_unique_places_visited_by_month = stats['num_of_unique_places_visited_by_month']

    # Convert the basic_stats_dict into a list containing a single dictionary
    basic_stats_list = [basic_stats_dict]
    months_list = stats['months_too_few_places_visited']
    min_num_of_unique_places_visited_per_month = stats['min_num_of_unique_places_visited_per_month']

    app = Dash(__name__)


    unique_years = sorted({month.split('_')[0]
                           for month in num_of_unique_places_visited_by_month})
    dropdown_options = [{'label': year, 'value': year}
                        for year in unique_years]
    dropdown_options.append({'label': 'All Years', 'value': 'All'})

    fig1 = px.histogram(
        x=num_of_unique_places_visited_by_month.values(),
        nbins=20,
        labels={'x': 'Number of Unique Places Visited'},
        title='Distribution of Monthly Unique Places Visited'
    )

    fig_line_chart = px.line(
        x=list(num_of_unique_places_visited_by_month.keys()),
        y=list(num_of_unique_places_visited_by_month.values()),
        labels={'x': 'Month', 'y': 'Number of Unique Places Visited'},
        title='Line Chart of Number of Unique Places Visited per Month'
    )

    basic_stats_section = html.Div(
        children=[html.H1(children="File Statistics"),
                  html.H2(children='Basic Statistics'),
                  dash_table.DataTable(
            id='basic_stats_table',
            columns=[
                {"name": "Number of Years of History", "id": "num_of_years"},
                {"name": "Number of Months of History", "id": "num_of_months"},
                {"name": "Number of Empty Files of History",
                 "id": "num_empty_files"},
                {"name": "Number of Empty Data Files of History",
                 "id": "num_empty_data_files"}
            ],
            data=basic_stats_list,
            page_size=10,
            style_cell={'textAlign': 'center',
                        'font-family': 'Times New Roman'}
        )]
    )

    month_with_too_few_places_visited_section = html.Div(
        children=[html.H2(children=f'Months with Fewer than {min_num_of_unique_places_visited_per_month} Places Visited'),
                  html.Ul([html.Li(month) for month in months_list]),])

    unique_places_visited_by_month_section = html.Div(
        children=[html.H2(children="Histogram of unique places visited by month"),
                  html.Div([html.Label("Select Year:"),
                            dcc.Dropdown(
                      id="year-dropdown",
                      options=dropdown_options,
                      value=None)
                  ]
        ),
            dcc.Graph(id='histogram', figure=fig1),
        ]
    )

    line_chart_section = html.Div([html.Div(children=[
        html.H2("Line Chart of Number of Unique Places Visited per Month"),
        html.Label("Select Year or All Years:"),
        dcc.Dropdown(
            id="year-dropdown-line-chart",
            options=dropdown_options,
            value=None
        )
    ]
    ),
        dcc.Graph(
        id='line-chart',
        figure=fig_line_chart
    )
    ]
    )

    app.layout = html.Div(
        children=[
            basic_stats_section,
            month_with_too_few_places_visited_section,
            unique_places_visited_by_month_section,
            line_chart_section
        ],
        style={'width': '90%', 'margin': 'auto'}
    )

    @app.callback(
        Output('histogram', 'figure'),
        [Input('year-dropdown', 'value')]
    )
    def update_histogram(selected_year):
        if selected_year and selected_year != 'All':
            data = [num_of_unique_places_visited_by_month[month]
                    for month in num_of_unique_places_visited_by_month if month.startswith(selected_year)]
        else:
            data = list(num_of_unique_places_visited_by_month.values())
        fig = px.histogram(
            x=data,
            nbins=20,
            labels={'x': 'Number of Unique Places Visited', 'y': 'Frequency'},
            title='Histogram of Unique Places Visited'
        )
        return fig

    @app.callback(
        Output('line-chart', 'figure'),
        [Input('year-dropdown-line-chart', 'value')]
    )
    def update_line_chart(selected_year):
        if selected_year and selected_year != 'All':
            months_in_year = [
                month for month in num_of_unique_places_visited_by_month if month.startswith(selected_year)]
            data = [num_of_unique_places_visited_by_month[month]
                    for month in months_in_year]
            fig = px.line(
                x=months_in_year,
                y=data,
                labels={'x': 'Month', 'y': 'Number of Unique Places Visited'},
                title=f'Line Chart of Number of Unique Places Visited per Month in {selected_year}'
            )
        else:
            fig = px.line(
                x=list(num_of_unique_places_visited_by_month.keys()),
                y=list(num_of_unique_places_visited_by_month.values()),
                labels={'x': 'Month', 'y': 'Number of Unique Places Visited'},
                title='Line Chart of Number of Unique Places Visited per Month'
            )
        return fig

    app.run(debug=True)
