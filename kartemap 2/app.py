# Tenzin Dasel and Kelly Zheng
# Assignment 1: Kartemap

from operator import itemgetter

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

traces = []

lon = 0
lat = 0

from dash.dependencies import Input, Output, State

# drop down list for use in airport codes
from controls import city_df, airlines_df, routes_df, airport_df

# setup app with stylesheets
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

# Create map template
mobileatlas_access_token = \
    'pk.eyJ1Ijoiam16aGVuZyIsImEiOiJja251dGpuOGUwZHoyMnRsZHJpcnhsNm9yIn0.h_3bdw8lVfKvqh6cN_31Jw'

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=8, r=5, b=5, t=5),  #where we are centering map
    hovermode='closest',
    mapbox=dict(
        accesstoken=mobileatlas_access_token,
        center=dict(lon=-98, lat=36),
        style="satellite",
        zoom=3.5,
    ),
)

colors = {
    'background': '#5c93ab',
    'header': '#074b69',
    'text': '#85C0FF'
}

#put different components into cards
gif = dbc.Card(
    dbc.CardImg(src='https://cdn.dribbble.com/users/914646/screenshots/3025059/aereo.gif', top=True),
)

controls_start_city = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Start City', className='text-white',),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in city_df['City']],
                    value='',
                    id='start-city',
                ),
            ]
        )
    ], color= colors['background']
)

controls_destination = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Destination City', className='text-white'),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in city_df['City']],
                    value='',
                    id='destination-city',
                    # disabled=True
                ),
            ]
        )
    ], color= colors['background']
)

controls_button = dbc.Card(
    [
        dbc.Button('Locate Route',
                   id='find-route-button',
                   outline=True, className='text-white')
    ], color= colors['background'],
    body=True,
)

description = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(md=2),
                dbc.Col(controls_start_city, md=3),
                dbc.Col(md=.5),
                # dbc.Col(controls_start_airport, md=3),
                dbc.Col(controls_destination, md=3),
                dbc.Col(md=.75),
                # dbc.Col(controls_destination_airport, md=3),
                dbc.Col(controls_button, md=3),
                dbc.Col(html.H2(), md=12),
                dbc.Col(gif, md=3),
                dbc.Col(
                    children="Webpage allows user to input start city and destination city and locates them on the "
                             "map below.",
                    style={"font-family": "system-ui", "fontSize": "24px", "color": "white", "text-align": "center"},
                ),
                dbc.Col(gif, md=3),
            ], align='center', className='bg-info'),
    ]
)

organization = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='map'), md=12),

            ],
            align='center', className='bg-info',
        ),
        dbc.Row(
            [
                dbc.Col(dash_table.DataTable(id='shortest-path-table'), md=12),
            ],
            align='center', className='bg-info',
        ),
        dbc.Row(
            [
                dbc.Col(html.H2(), md=3),
                dbc.Col(
                    html.H6('Copyright (C) 2021, Python and Applications to Business Analytics II, '
                            'Tenzin Dasel and Kelly Zheng, All Rights Reserved.',
                            className='text-white'), md=9
                )
            ], align='center', className='bg-info'),
    ]
)


app.layout = html.Div(children=[
    html.H1('Kartemap - Flight Route Analysis', style = {'background-color': colors['header'], 'color': 'white', 'font-size': '25px'}),
    description,
    organization
]
)


# airline selected, populate and enable start and destination city controls
#
'''@app.callback([Output('start-city', 'options'),
               Output('start-city', 'disabled'),
               Output('destination-city', 'options'),
               Output('destination-city', 'disabled')],
              [Input('airline', 'value')])'''
def populate_city_controls_after_airline_selected(airline):
    if airline == '':
        return [], True, [], True

    # retrieve the airline_id for the selected airline
    selected_airline_as_list = airlines_df.query(f'Name=="{airline}"')['Airline_id'].tolist()
    airline_id = selected_airline_as_list[0]

    # get all routes for the selected airline
    airline_routes_df = routes_df.copy()
    airline_routes_df = airline_routes_df.query(f'Airline_id=="{airline_id}"')

    # get city name for start and destination airports
    start_airport_ids = airline_routes_df['Source_airport_id'].to_list()
    start_city_df = airport_df[airport_df['Airport_id'].isin(start_airport_ids)]

    # populate source and destination city list for the dropdown controls
    destination_airport_ids = list(airline_routes_df['Destination_airport_id'])
    destination_city_df = airport_df[airport_df['Airport_id'].isin(destination_airport_ids)]

    start_city_options = [{'label': col, 'value': col} for col in start_city_df['City']]
    start_city_options = sorted(start_city_options, key=itemgetter('value'))
    destination_city_options = [{'label': col, 'value': col} for col in destination_city_df[
        'City']]
    destination_city_options = sorted(destination_city_options, key=itemgetter('value'))

    return start_city_options, False, destination_city_options, False


# start or destination city selected, populate start or destination airport
#
@app.callback([Output('start-city-airport', 'options'),
               Output('start-city-airport', 'disabled'),
               Output('destination-city-airport', 'options'),
               Output('destination-city-airport', 'disabled')],
              [Input('airline', 'value'),
               Input('start-city', 'value'),
               Input('destination-city', 'value')])

def populate_airport_controls_after_city_selected(start_city, destination_city):
    if start_city == '':
        start_city_airport_options = []
        start_city_airport_disable = True
    else:
        # retrieve the airline_id for a given airline name
        ctl_routes_df = routes_df.copy()
        #selected_airline_as_list = airlines_df.query(f'Name=="{airline}"')['Airline_id'].tolist()
        #airline_id = selected_airline_as_list[0]

        # get all routes for the selected airline
        #ctl_routes_df = ctl_routes_df.query(f'Airline_id=="{airline_id}"')

        # get source airport
        #source_airport_ids = ctl_routes_df['Source_airport_id'].to_list()
        #ctl_src_airport_df = airport_df[airport_df['Airport_id'].isin(source_airport_ids)]
        #ctl_src_airport_df = ctl_src_airport_df.query(f'City=="{start_city}"')
        start_city_airport_options = [{'label': col, 'value': col} for col in
                                      ctl_src_airport_df['Name']]
        start_city_airport_options.sort()
        start_city_airport_disable = False

    if destination_city == '':
        destination_city_airport_options = []
        destination_city_airport_disable = True
    else:
        # retrieve the airline_id for a given airline name
        ctl_routes_df = routes_df.copy()
        #selected_airline_as_list = airlines_df.query(f'Name=="{airline}"')['Airline_id'].tolist()
        #airline_id = selected_airline_as_list[0]

        # get all routes for the selected airline
        #ctl_routes_df = ctl_routes_df.query(f'Airline_id=="{airline_id}"')

        # get destination airport
        destination_airport_ids = ctl_routes_df['Destination_airport_id'].to_list()
        ctl_dest_airport_df = airport_df[airport_df['Airport_id'].isin(destination_airport_ids)]
        ctl_dest_airport_df = ctl_dest_airport_df.query(f'City=="{destination_city}"')
        destination_city_airport_options = [{'label': col, 'value': col} for col in
                                            ctl_dest_airport_df['Name']]
        destination_city_airport_options.sort()
        destination_city_airport_disable = False

    #return start_city_airport_options, start_city_airport_disable, \
    #      destination_city_airport_options, destination_city_airport_disable


@app.callback(Output('map', 'figure'),
              [Input('start-city', 'value'),
               Input('destination-city', 'value')],
              [State('map', 'relayoutData')])
def make_map(start_city, destination_city, map_layout):
    global traces
    for name, df in airport_df.groupby('City'):
        trace = dict(
            type='scattermapbox',
            lon=df['Longitude'],
            lat=df['Latitude'],
            text=df['City'],
            showlegend=False,
            marker=dict(
                size=30 if name in [start_city, destination_city] else 5,
                opacity=0.95 if name in [start_city, destination_city] else 0.65,
                symbol='airport',
                color='brown' if name in [start_city, destination_city] else 'yellow',
            ),
            visible=True
        )
        traces.append(trace)

    # relayoutData is None by default, and {'autosize': True} without relayout action
    if map_layout is not None:
        if 'mapbox.center' in map_layout.keys():
            lon = float(map_layout['mapbox.center']['lon'])
            lat = float(map_layout['mapbox.center']['lat'])
            zoom = float(map_layout['mapbox.zoom'])
            layout['mapbox']['center']['lon'] = lon
            layout['mapbox']['center']['lat'] = lat
            layout['mapbox']['zoom'] = zoom

    figure = dict(data=traces, layout=layout)
    return figure


@app.callback(Output('shortest-path-table', 'data'),
              [Input('start-city-airport', 'value'),
               Input('destination-city-airport', 'value')])

def find_shortest_route(start_city_airport, destination_city_airport):
    '''cities, distances = Network.main.read_network_from_file(traces)
    #network = Network.graph.main(traces,)

    network = Network()
    network.add_nodes(cities)

    for connection in distances.items():
        frm = cities[connection[0]]
        for connection_to in connection[1].items():
            network.add_edge(frm, cities[connection_to[0]], connection_to[1])

    # uncomment to print the network
    # print(network)

    # get from user the start city
    for (index, city) in enumerate(network.get_nodes()):
        print(f'{index}: {city:s}')
    start_city_index = int(input(
        f'What is the start city by index (0 to {len(network.get_nodes()) - 1})? '))
    start_city = network.get_nodes()[start_city_index]

    # using Dijkstra's algorithm, compute least cost (distance)
    # from start city to all other cities
    Dijkstra.compute(network, network.get_node(start_city))

    # show the shortest path(s) from start city to all other cities
    print('\nShortest Paths')
    for target_node in network.get_nodes():
        target_city = network.get_node(target_node)
        if target_city.get_name() == end_city:
            path = [target_city.get_name()]
            Dijkstra.compute_shortest_path(target_city, path)
            print(f'{start_city} -> {target_node} = {path[::-1]} : {target_city.get_weight():6.0f}')
            shortest_path = [path::-1]

            leg, s_city, s_airport, e_city, e_airport, distance = [], [], [], [], \
                                                                  [], []

            for index in range(1, len(shortest_path)):
                leg.append(index)
                s_city.append(shortest_path[index-1])
                s_airport.append('AAA')
                e_city.append(shortest_path[index])
                e_airport.append('BBB')
                distance.append(0.0)

            shortest_path_routes_df.from_dict(
                {
                    "Leg": leg,
                    "Start City": s_city,
                    "Start Airport": s_airport,
                    "End City": e_city,
                    "End Airport": e_airport,
                    "Distance": distance
                }
            )'''

    pass


if __name__ == '__main__':
    app.run_server(debug=True)
