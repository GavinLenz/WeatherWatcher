from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
from flask import Flask
from LocationScript import update_weather_data
import pandas as pd
from datetime import datetime, timedelta

flask_app = Flask(__name__)


def create_dash_application(flask_app):
    # Add external Bootstrap stylesheet
    dash_app = Dash(
        server=flask_app,
        routes_pathname_prefix='/dash/',
        external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css']
    )

    dash_app.layout = html.Div([
        html.Div([
            html.H1("Weather Data for Multiple Cities", className="text-center mb-4",
                    style={'font-size': '2.5rem', 'font-weight': 'bold'}),

            html.Div([
                dcc.Checklist(
                    id='city-selector',
                    options=[{'label': city, 'value': city} for city in update_weather_data()['City'].unique()],
                    value=update_weather_data()['City'].unique(),
                    inline=False,
                    style={
                        'display': 'flex',
                        'flex-wrap': 'wrap',
                        'justify-content': 'center',
                        'gap': '15px',
                        'font-size': '1.2rem'
                    }
                ),
            ], className="mb-3", style={'margin-bottom': '30px', 'padding': '20px'}),

            # Graph for Temperature
            html.Div([
                dcc.Graph(id='temperature-graph', style={'border': '1px solid #ddd', 'border-radius': '10px',
                                                         'box-shadow': '0px 4px 8px rgba(0,0,0,0.1)'})
            ], className="mb-5", style={'padding': '20px', 'background-color': '#f9f9f9'}),

            # Graph for Humidity
            html.Div([
                dcc.Graph(id='humidity-graph', style={'border': '1px solid #ddd', 'border-radius': '10px',
                                                      'box-shadow': '0px 4px 8px rgba(0,0,0,0.1)'})
            ], className="mb-5", style={'padding': '20px', 'background-color': '#f9f9f9'}),
        ], className="container-fluid"),

        # Interval for refreshing data
        dcc.Interval(id='interval-component', interval=5 * 1000, n_intervals=0)
    ], style={'background-color': '#f0f2f5', 'padding': '40px 0'})  # Full-page background and padding

    # Callback to update both Temperature and Humidity graphs
    @dash_app.callback(
        [Output('temperature-graph', 'figure'),
         Output('humidity-graph', 'figure')],
        [Input('city-selector', 'value'),
         Input('interval-component', 'n_intervals')]
    )
    def update_weather_graph(selected_cities, n):
        df = update_weather_data()  # Get the latest weather data

        # Filter for last 24 hours (cap scrolling to 24 hours)
        now = datetime.now()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df[df['Timestamp'] >= now - timedelta(hours=24)]

        temperature_fig = go.Figure()
        humidity_fig = go.Figure()

        # Plot Temperature for each selected city
        for city in selected_cities:
            city_data = df[df['City'] == city].sort_values('Timestamp')
            temperature_fig.add_trace(go.Scatter(
                x=city_data['Timestamp'], y=city_data['Temperature (°F)'],
                mode='lines', name=city
            ))

        # Customize temperature graph layout
        temperature_fig.update_layout(
            title="Temperature Over Time by City (Last 24 Hours)",
            xaxis_title="Time",
            yaxis_title="Temperature (°F)",
            hovermode="x unified",
            plot_bgcolor='#ffffff',
            paper_bgcolor='#f9f9f9',
            margin=dict(t=50, b=40, l=50, r=0),
            xaxis = dict(
                range=[now - timedelta(hours=24), now],
                fixedrange=True
            )
        )

        # Plot Humidity for each selected city
        for city in selected_cities:
            city_data = df[df['City'] == city].sort_values('Timestamp')
            humidity_fig.add_trace(go.Scatter(
                x=city_data['Timestamp'], y=city_data['Humidity (%)'],
                mode='lines', name=city
            ))

        # Customize humidity graph layout
        humidity_fig.update_layout(
            title="Humidity Over Time by City (Last 24 Hours)",
            xaxis_title="Time",
            yaxis_title="Humidity (%)",
            hovermode="x unified",
            plot_bgcolor='#ffffff',
            paper_bgcolor='#f9f9f9',
            margin=dict(t=50, b=40, l=50, r=0),
            xaxis = dict(
                range=[now - timedelta(hours=24), now],
                fixedrange=True
            )
        )

        return temperature_fig, humidity_fig

    return dash_app


create_dash_application(flask_app)

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=8000, debug=True)