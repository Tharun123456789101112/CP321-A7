#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"

tables = pd.read_html(url)

world_cup_table = tables[3]

world_cup_table.columns = ['Year', 'Winner', 'Score', 'Runner-Up', 'Venue', 'Location', 'Attendance', 'Ref']

world_cup_cleaned = world_cup_table[['Year', 'Winner', 'Runner-Up']]

world_cup_cleaned.loc[:, 'Winner'] = world_cup_cleaned['Winner'].replace("West Germany", "Germany")
world_cup_cleaned.loc[:, 'Runner-Up'] = world_cup_cleaned['Runner-Up'].replace("West Germany", "Germany")

winning_countries = world_cup_cleaned['Winner'].unique()

winning_countries = [country for country in winning_countries if country and pd.notna(country)]

app = dash.Dash(__name__)

server = app.server
app.layout = html.Div([
    html.H1("FIFA World Cup Winners and Runner-Ups"),
    
    # Dropdown for selecting a country
    html.Label("Select a Country:"),
    dcc.Dropdown(
        id="country-dropdown",
        options=[{"label": country, "value": country} for country in winning_countries],
        value=winning_countries[0],
    ),
    
    html.Div(id="country-wins"),

    # Dropdown for selecting a year
    html.Label("Select a Year:"),
    dcc.Dropdown(
        id="year-dropdown",
        options=[{"label": year, "value": year} for year in world_cup_cleaned['Year'].unique()],
        value=world_cup_cleaned['Year'].iloc[0],  # Default value
    ),
    
    html.Div(id="year-result"),

    # Display World Cup roles on a choropleth map
    dcc.Graph(id="choropleth-map"),

    # New Section to display all countries that have won a World Cup
    html.Div([
        html.H3("Countries that have won the World Cup:"),
        html.Ul([html.Li(country) for country in winning_countries])
    ], style={"marginTop": "30px", "marginBottom": "20px"})
])

@app.callback(
    Output("country-wins", "children"),
    [Input("country-dropdown", "value")]
)
def display_wins(country):
    wins = world_cup_cleaned[world_cup_cleaned['Winner'] == country].shape[0]
    return f"{country} has won the World Cup {wins} times."

@app.callback(
    Output("year-result", "children"),
    [Input("year-dropdown", "value")]
)
def display_result(year):
    result = world_cup_cleaned[world_cup_cleaned['Year'] == year]
    winner = result['Winner'].iloc[0]
    runner_up = result['Runner-Up'].iloc[0]
    return f"In {year}, the Winner was {winner} and the Runner-Up was {runner_up}."

@app.callback(
    Output("choropleth-map", "figure"),
    [Input("year-dropdown", "value")]
)
def update_choropleth(year):
    data = world_cup_cleaned[world_cup_cleaned['Year'] == year]
    winner = data['Winner'].iloc[0]
    runner_up = data['Runner-Up'].iloc[0]
    
    map_data = pd.DataFrame({
        'Country': [winner, runner_up],
        'Role': ['Winner', 'Runner-Up'],
        'Value': [1, 2] 
    })
    
    fig = px.choropleth(
        map_data,
        locations='Country',
        locationmode='country names',
        color='Value',
        hover_name='Country',
        hover_data=['Role'],
        color_continuous_scale=["blue", "red"],
        title=f"World Cup Winner and Runner-Up in {year}",
        labels={'Value': 'World Cup Role'}
    )

    fig.update_layout(
        coloraxis_colorbar=dict(
            tickvals=[1, 2],
            ticktext=["Winner", "Runner-Up"],
            title="World Cup Role"
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)


# In[ ]:




