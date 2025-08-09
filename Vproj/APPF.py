import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State
import dash.exceptions
import os
from math import log
import plotly.graph_objects as go

app = dash.Dash(__name__, suppress_callback_exceptions=True)

server = app.server

CSV_PATH = r"C:\Users\kubag\Desktop\Vproj\cleaned_pokemon.csv"

def load_pokemon_data():
    try:
        print(f"Attempting to load data from: {CSV_PATH}")
        
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"File not found at: {CSV_PATH}")
        
        df = pd.read_csv(CSV_PATH)
        print(f"Successfully loaded {len(df)} Pokémon records")
        
        required_columns = ['id', 'name', 'evolution_chain_id', 'sprite_url', 
                          'type_1', 'type_2', 'abilities', 'height', 'weight',
                          'hp', 'attack', 'defense', 'special-attack', 
                          'special-defense', 'speed']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        numeric_cols = ['id', 'evolution_chain_id', 'hp', 'attack', 'defense', 
                       'special-attack', 'special-defense', 'speed', 'height', 'weight']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.sort_values("id")
        
    except Exception as e:
        print(f"\nERROR LOADING DATA: {str(e)}")
        return pd.DataFrame()
def create_gallery_view(df):
    filtered_df = df[df["type_1"].notna()]
    cards = []

    for _, row in filtered_df.iterrows():
        cards.append(html.Div([
            html.Img(
                src=row["sprite_url"],
                id={'type': 'gallery_img', 'index': int(row["id"])},
                style={
                    'height': '100px',
                    'width': '100px',
                    'cursor': 'pointer',
                    'borderRadius': '10px',
                    'border': '2px solid transparent',
                    'transition': 'transform 0.2s',
                }
            ),
            html.Div(row["name"].capitalize(), style={'textAlign': 'center', 'marginTop': '5px'})
        ], style={'textAlign': 'center', 'width': '120px', 'margin': '10px'}))

    return html.Div(cards, style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'justifyContent': 'center',
        'gap': '10px'
    })

df = load_pokemon_data()
pokemon_options = [{"label": row["name"].capitalize(), "value": row["id"]} 
                  for _, row in df.iterrows()] if not df.empty else []
id_to_name = dict(zip(df["id"], df["name"])) if not df.empty else {}
name_to_id = dict(zip(df["name"], df["id"])) if not df.empty else {}

def create_evolution_tree(pokemon_id, df):
    try:
        p = df[df["id"] == pokemon_id].iloc[0]
        if 'evolution_chain_id' not in p or pd.isna(p['evolution_chain_id']):
            return None
            
        family = df[df["evolution_chain_id"] == p["evolution_chain_id"]]
        if "evolution_stage" in family.columns:
            family = family.sort_values("evolution_stage")
        
        stages = family['evolution_stage'].unique()
        tree = []
        
        for stage in sorted(stages):
            stage_pokemon = family[family['evolution_stage'] == stage]
            stage_nodes = []
            
            for _, evo in stage_pokemon.iterrows():
                is_current = evo["id"] == pokemon_id
                node = html.Div([
                    html.Img(
                        src=evo["sprite_url"],
                        style={
                            "height": "70px",
                            "width": "70px",
                            "borderRadius": "50%",
                            "border": "3px solid orange" if is_current else "2px solid #aaa",
                            "margin": "5px auto",
                            "cursor": "pointer",
                            "background": "white",
                            "display": "block"
                        },
                        id={'type': 'evo_img', 'index': int(evo["id"])}
                    ),
                    html.Div(
                        evo["name"].capitalize(), 
                        style={
                            "textAlign": "center",
                            "fontSize": "14px",
                            "fontWeight": "bold" if is_current else "normal",
                            "marginBottom": "10px"
                        }
                    )
                ])
                stage_nodes.append(node)
            
            tree.append(html.Div(
                stage_nodes,
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "20px"
                }
            ))
            
            if stage != max(stages):
                tree.append(html.Div(
                    style={
                        'width': '2px',
                        'height': '30px',
                        'background': '#aaa',
                        'margin': '0 auto',
                        'position': 'relative',
                        'zIndex': 1
                    }
                ))
                
        return html.Div(
            tree,
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'padding': '20px'
            }
        )
        
    except Exception as e:
        print(f"Error creating evolution tree: {e}")
        return None

        import plotly.graph_objects as go
def create_stat_variability_histogram(df):
    from dash import dcc, html

    stat_options = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']

    return html.Div([
        html.Label("Select Stat:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='stat_dropdown',
            options=[{'label': stat.replace("-", " ").capitalize(), 'value': stat} for stat in stat_options],
            value='attack',
            style={'width': '300px', 'marginBottom': '20px'}
        ),
        dcc.Graph(id='stat_histogram')
    ], style={'maxWidth': '500px', 'margin': '0 auto'})


def create_capture_difficulty_gauge(pokemon):
    capture_rate = pokemon.get('capture_rate', None)
    if capture_rate is None:
        return html.Div("Capture rate data not available.")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=capture_rate,
        title={'text': "Capture Difficulty"},
        gauge={
            'axis': {'range': [0, 255]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 85], 'color': "red"},
                {'range': [85, 170], 'color': "yellow"},
                {'range': [170, 255], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': capture_rate
            }
        }
    ))

    return dcc.Graph(figure=fig, style={'height': '350px'})





def create_stat_bars(p1, p2):
    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
    stat_names = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=stat_names,
        y=[p1[s] for s in stats],
        name=p1['name'].capitalize(),
        marker_color='#FFA500',
        width=0.4
    ))
    
    fig.add_trace(go.Bar(
        x=stat_names,
        y=[p2[s] for s in stats],
        name=p2['name'].capitalize(),
        marker_color='#1E90FF',
        width=0.4
    ))
    
    fig.update_layout(
        barmode='group',
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        yaxis=dict(
            title="Stat Value",
            range=[0, max(max(p1[s] for s in stats), max(p2[s] for s in stats)) * 1.2]
        ),
        xaxis=dict(title="Stat")
    )
    
    return dcc.Graph(figure=fig, style={'height': '350px'})

def create_happiness_scatter(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['hatch_counter'],
        y=df['base_happiness'],
        mode='markers',
        text=df['name'],
        marker=dict(
            size=10,
            color='rgba(30,144,255,0.6)',
            line=dict(width=1, color='darkblue')
        ),
        hovertemplate="<b>%{text}</b><br>Hatch Counter: %{x}<br>Happiness: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title='Base Happiness vs Hatch Counter',
        xaxis_title='Hatch Counter (Steps to Hatch)',
        yaxis_title='Base Happiness',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return dcc.Graph(figure=fig, style={'width': '100%', 'maxWidth': '600px', 'margin': '0 auto'})


def create_comparison_view(pokemon1_id, pokemon2_id, df):
    if pokemon1_id is None or pokemon2_id is None:
        return html.Div("Select two Pokémon to compare", style={'textAlign': 'center', 'padding': '20px'})
    
    p1 = df[df["id"] == pokemon1_id].iloc[0]
    p2 = df[df["id"] == pokemon2_id].iloc[0]
    
    base_size = 200 
    if p1['height'] >= p2['height']:
        size1 = base_size
        size2 = base_size * (p2['height'] / p1['height'])
        size_ratio = f"Size ratio: 1 : {p2['height']/p1['height']:.2f}"
    else:
        size2 = base_size
        size1 = base_size * (p1['height'] / p2['height'])
        size_ratio = f"Size ratio: {p1['height']/p2['height']:.2f} : 1"
    
    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
    stat_values1 = [int(p1[s]) for s in stats]
    stat_values2 = [int(p2[s]) for s in stats]
    stats += [stats[0]] 
    stat_values1 += [stat_values1[0]]
    stat_values2 += [stat_values2[0]]
    
    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=stat_values1,
        theta=[s.upper() for s in stats],
        fill='toself',
        name=p1['name'].capitalize(),
        line=dict(color='#FFA500'),
        fillcolor='rgba(255, 165, 0, 0.4)'
    ))
    radar.add_trace(go.Scatterpolar(
        r=stat_values2,
        theta=[s.upper() for s in stats],
        fill='toself',
        name=p2['name'].capitalize(),
        line=dict(color='#1E90FF'),
        fillcolor='rgba(30, 144, 255, 0.4)'
    ))
    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(stat_values1[:-1]), max(stat_values2[:-1])) + 20]
            )
        ),
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40),
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5
        )
    )
    
    stat_bars = create_stat_bars(p1, p2)
    
    return html.Div([
        html.Div([
            html.Div([
                html.H3("Pokémon Comparison", style={'textAlign': 'center', 'marginBottom': '20px'}),
                html.Div([
                    html.Div([
                        html.Img(
                            src=p1["sprite_url"],
                            style={
                                'height': f'{size1}px',
                                'width': f'{size1}px',
                                'margin': '0 auto',
                                'display': 'block'
                            }
                        ),
                        html.H4(p1["name"].capitalize(), style={'textAlign': 'center', 'color': '#FFA500'}),
                        html.Div(f"Height: {p1['height']} dm", style={'textAlign': 'center'})
                    ], style={'flex': 1, 'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                    
                    html.Div([
                        html.Div(size_ratio, style={
                            'textAlign': 'center',
                            'fontWeight': 'bold',
                            'margin': '20px 0',
                            'padding': '10px',
                            'backgroundColor': '#f0f0f0',
                            'borderRadius': '5px'
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    
                    html.Div([
                        html.Img(
                            src=p2["sprite_url"],
                            style={
                                'height': f'{size2}px',
                                'width': f'{size2}px',
                                'margin': '0 auto',
                                'display': 'block'
                            }
                        ),
                        html.H4(p2["name"].capitalize(), style={'textAlign': 'center', 'color': '#1E90FF'}),
                        html.Div(f"Height: {p2['height']} dm", style={'textAlign': 'center'})
                    ], style={'flex': 1, 'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-end'}),
                
                dcc.Graph(figure=radar, style={'height': '350px'}),

                
                
                html.H4("Stat Comparison", style={
                    'textAlign': 'center',
                    'marginTop': '30px',
                    'marginBottom': '10px',
                    'borderBottom': '2px solid #eee',
                    'paddingBottom': '10px'
                }),
                
                stat_bars,
                
                html.Div([
                    html.Button("Back to Single View", id="back_button", n_clicks=0, 
                              style={'margin': '10px', 'padding': '10px 20px', 'backgroundColor': '#FFA500', 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
                ], style={'textAlign': 'center'})
            ], style={'padding': '20px'})
        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})
    ])

app.layout = html.Div(


    style={
        'backgroundColor': '#f9f9f9',
        'minHeight': '100vh',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif'
    },
    children=[
        dcc.Store(id='comparison_store', data={'pokemon1': None, 'pokemon2': None}),
        dcc.Store(id='selected_pokemon_id', data=None), 
        html.H1(
            "Pokémon Dashboard",
            style={
                'textAlign': 'center',
                'color': '#333',
                'marginBottom': '30px'
            }
        ),
        
        html.Div(id='comparison_indicator', style={
            'position': 'fixed',
            'top': '20px',
            'right': '20px',
            'backgroundColor': 'white',
            'padding': '10px',
            'borderRadius': '5px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.2)',
            'zIndex': 1000
        }),
        
        html.Div(
    id='dropdown_container',
    children=[
        html.Label(
            "Select Pokémon:",
            style={
                'display': 'block',
                'marginBottom': '10px',
                'fontWeight': 'bold'
            }
        ),
        dcc.Dropdown(
            id='pokemon_dropdown',
            options=pokemon_options,
            value=None,
            disabled=df.empty,
            style={
                'width': '100%',
                'maxWidth': '400px',
                'margin': '0 auto'
            }
        )
    ],
    style={
        'width': '100%',
        'maxWidth': '800px',
        'margin': '0 auto 30px',
        'display': 'none' 
    }
),

        
        html.Div(
            id='pokemon_content',
            style={
                'maxWidth': '1200px',
                'margin': '0 auto',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'padding': '20px',
                'minHeight': '500px'
            }
        )
    ]
)



@app.callback(
    Output('dropdown_container', 'style'),
    [Input('selected_pokemon_id', 'data')],
)
def toggle_dropdown_visibility(selected_id):
    if selected_id is None:
        return {'display': 'none'}
    return {
        'width': '100%',
        'maxWidth': '800px',
        'margin': '0 auto 30px',
        'display': 'block'
    }


@app.callback(
    Output('comparison_indicator', 'children'),
    [Input('comparison_store', 'data')]
)
def update_comparison_indicator(comparison_data):
    if comparison_data['pokemon1'] is None and comparison_data['pokemon2'] is None:
        return "No Pokémon selected for comparison"
    
    selected = []
    if comparison_data['pokemon1']:
        name1 = df[df['id'] == comparison_data['pokemon1']].iloc[0]['name'].capitalize()
        selected.append(html.Span(name1, style={'color': '#FFA500', 'fontWeight': 'bold'}))
    if comparison_data['pokemon2']:
        name2 = df[df['id'] == comparison_data['pokemon2']].iloc[0]['name'].capitalize()
        selected.append(html.Span(name2, style={'color': '#1E90FF', 'fontWeight': 'bold'}))
    
    if len(selected) == 1:
        return [html.Span("Selected for comparison: "), selected[0]]
    elif len(selected) == 2:
        return [html.Span("Comparing: "), selected[0], html.Span(" vs "), selected[1]]
    else:
        return "No Pokémon selected for comparison"

@app.callback(
    Output('pokemon_content', 'children'),
    [Input('pokemon_dropdown', 'value'),
     Input('comparison_store', 'data'),
     Input('selected_pokemon_id', 'data')],
    prevent_initial_call=False
)
def update_display(pokemon_id, comparison_data, selected_id):
    if pokemon_id is None and selected_id is not None:
        pokemon_id = selected_id

    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'comparison_store' and comparison_data['pokemon1'] and comparison_data['pokemon2']:
        return create_comparison_view(comparison_data['pokemon1'], comparison_data['pokemon2'], df)
    
    try:
        if df.empty:
            return html.Div(
                "Pokémon data could not be loaded. Please check your data files.",
                style={
                    'textAlign': 'center',
                    'color': 'red',
                    'padding': '40px'
                }
            )
            
        if pokemon_id is None or pokemon_id not in df['id'].values:
            return create_gallery_view(df)
            
        p = df[df["id"] == pokemon_id].iloc[0]

        type_counts = df['type_1'].value_counts().sort_values(ascending=False)

        type_donut = dcc.Graph(
            id='type_donut',
            figure={
                'data': [go.Pie(
                    labels=type_counts.index.str.capitalize(),
                    values=type_counts.values,
                    hole=0.4,
                    marker=dict(line=dict(color='white', width=2)),
                    textinfo='none', 
                    hoverinfo='label+percent'
                )],
                'layout': go.Layout(
                    title="Primary Type Distribution",
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        x=1,
                        y=0.5,
                        xanchor='left',
                        yanchor='middle'
                    ),
                    margin=dict(l=20, r=100, t=40, b=20),
                    height=500
                )
            },
            config={'displayModeBar': False}
        )

        
        stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
        stat_values = [int(p[s]) for s in stats]
        stats += [stats[0]] 
        stat_values += [stat_values[0]]
        
        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=stat_values,
            theta=[s.upper() for s in stats],
            fill='toself',
            line=dict(color='#FFA500'),
            fillcolor='rgba(255, 165, 0, 0.4)'
        ))
        radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(stat_values[:-1]) + 20]
                )
            ),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40),
            height=350
        )

        
        evolution_tree = create_evolution_tree(pokemon_id, df)

        gender_dist = p.get("gender_distribution", "Genderless")
        gender_labels = []
        gender_values = []
        colors = ['#3498db', '#e74c3c', '#95a5a6']

        if "Male" in gender_dist and "Female" in gender_dist:
            male_pct = int(gender_dist.split('%')[0])
            female_pct = 100 - male_pct
            gender_labels = ['Male', 'Female']
            gender_values = [male_pct, female_pct]
        elif "Male" in gender_dist:
            gender_labels = ['Male']
            gender_values = [100]
        elif "Female" in gender_dist:
            gender_labels = ['Female']
            gender_values = [100]
        else:
            gender_labels = ['Genderless']
            gender_values = [100]

        gender_pie = dcc.Graph(
    id='gender_pie',
    figure={
        'data': [{
            'type': 'pie',
            'labels': gender_labels,
            'values': gender_values,
            'hoverinfo': 'label+percent',
            'textinfo': 'label+percent',
            'marker': {
                'colors': colors[:len(gender_labels)],
                'line': {'color': 'white', 'width': 2}
            }
        }],
        'layout': {
            'title': 'Gender Distribution',
            'paper_bgcolor': '#f9f9f9',
            'plot_bgcolor': '#f9f9f9',
            'margin': {'l': 20, 'r': 20, 't': 30, 'b': 20},
            'hovermode': 'closest'
        }
    },
    style={'width': '300px', 'margin': '20px auto'}
)


        capture_difficulty_gauge = create_capture_difficulty_gauge(p)

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
    [
        html.Div(
            [
                html.H2(
                    p["name"].capitalize(),
                    style={'color': '#333', 'marginBottom': '10px'}
                ),
                html.Img(
                    src=p["sprite_url"],
                    style={
                        'height': '200px',
                        'width': '200px',
                        'marginBottom': '20px',
                        'cursor': 'pointer',
                        'border': '3px solid #FFA500' if comparison_data['pokemon1'] == pokemon_id or comparison_data['pokemon2'] == pokemon_id else '3px solid transparent',
                        'transition': 'border 0.3s ease'
                    },
                    id={'type': 'pokemon_img', 'index': int(p["id"])}
                ),
                html.P(f"Height: {p['height']} dm | Weight: {p['weight']} hg", style={'marginBottom': '10px'}),
                html.P(f"Abilities: {p['abilities']}", style={'marginBottom': '10px'}),
                html.P(f"Type: {p['type_1'].capitalize()}" + (f" / {p['type_2'].capitalize()}" if pd.notna(p['type_2']) else ""), style={'marginBottom': '20px'}),
                dcc.Graph(figure=radar, style={'height': '350px'})
            ],
            style={'flex': '1', 'padding': '20px', 'minWidth': '320px'}
        ),

        html.Div(
            [
                html.H3("Evolution Chain", style={
                    'borderBottom': '2px solid #eee',
                    'paddingBottom': '10px',
                    'marginBottom': '20px'
                }),
                evolution_tree if evolution_tree else html.Div(
                    "No evolution data available",
                    style={'textAlign': 'center', 'color': '#999', 'padding': '40px'}
                )
            ],
            style={'flex': '1', 'padding': '10px', 'minWidth': '220px', 'maxWidth': '250px'}
        ),

        html.Div(
            [
                html.Div(capture_difficulty_gauge, style={'marginBottom': '20px'}),
                html.Div(create_happiness_scatter(df))
            ],
            style={'flex': '1', 'padding': '10px', 'minWidth': '320px'}
        )
    ],
    style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'justifyContent': 'center'
    }
),

                    ],
                    style={
                        'display': 'flex',
                        'flexWrap': 'wrap'
                    }
                ),
                html.Hr(style={'margin': '40px 0', 'borderTop': '2px solid #ccc'}),


                html.Div(
                    [
                        html.Div(
                            gender_pie,
                            style={'flex': '1', 'padding': '10px', 'minWidth': '300px'}
                        ),
                        html.Div(
                            [
                                type_donut,
                                html.Div(id='type_sprites', style={
                                    'display': 'flex',
                                    'flexWrap': 'wrap',
                                    'justifyContent': 'center',
                                    'gap': '10px',
                                    'marginTop': '10px',
                                    'maxWidth': '450px'
                                })
                            ],
                            style={
                                'flex': '1',
                                'padding': '10px',
                                'minWidth': '400px',
                                'maxWidth': '500px'
                            }
                        ),
                        html.Div(
                            create_stat_variability_histogram(df),
                            style={'flex': '1', 'padding': '10px', 'minWidth': '300px'}
                        )
                    ],
                    style={
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'justifyContent': 'center'
                    }
                )

            ]
        )

        
    except Exception as e:
        print(f"Error in update_display: {e}")
        return html.Div(
            [
                html.H3("Error displaying Pokémon data", style={'color': 'red'}),
                html.P(str(e))
            ],
            style={
                'padding': '20px',
                'color': 'red'
            }
        )

@app.callback(
    Output('pokemon_dropdown', 'value'),
    [Input({'type': 'evo_img', 'index': dash.ALL}, 'n_clicks')],
    [State({'type': 'evo_img', 'index': dash.ALL}, 'id')],
    prevent_initial_call=True
)
def change_pokemon(n_clicks_list, ids):
    if not n_clicks_list or all(click is None for click in n_clicks_list):
        raise dash.exceptions.PreventUpdate
        
    try:
        valid_clicks = [(i, click) for i, click in enumerate(n_clicks_list) if click is not None]
        if not valid_clicks:
            raise dash.exceptions.PreventUpdate
            
        clicked_index = max(valid_clicks, key=lambda x: x[1])[0]
        return ids[clicked_index]['index']
    except:
        raise dash.exceptions.PreventUpdate

@app.callback(
    Output('comparison_store', 'data'),
    [Input({'type': 'pokemon_img', 'index': dash.ALL}, 'n_clicks')],
    [State({'type': 'pokemon_img', 'index': dash.ALL}, 'id'),
     State('comparison_store', 'data')],
    prevent_initial_call=True
)



def add_to_comparison(n_clicks_list, ids, current_data):
    if not n_clicks_list or all(click is None for click in n_clicks_list):
        raise dash.exceptions.PreventUpdate
        
    try:
        valid_clicks = [(i, click) for i, click in enumerate(n_clicks_list) if click is not None]
        if not valid_clicks:
            raise dash.exceptions.PreventUpdate
            
        clicked_index = max(valid_clicks, key=lambda x: x[1])[0]
        clicked_id = ids[clicked_index]['index']
        
        if current_data['pokemon1'] is None:
            current_data['pokemon1'] = clicked_id
        elif current_data['pokemon2'] is None and clicked_id != current_data['pokemon1']:
            current_data['pokemon2'] = clicked_id
        else:
            current_data = {'pokemon1': clicked_id, 'pokemon2': None}
            
        return current_data
    except:
        raise dash.exceptions.PreventUpdate

@app.callback(
    Output('comparison_store', 'data', allow_duplicate=True),
    [Input('back_button', 'n_clicks')],
    prevent_initial_call=True
)
def back_to_single_view(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
        
    return {'pokemon1': None, 'pokemon2': None}

@app.callback(
    Output('selected_pokemon_id', 'data'),
    Input({'type': 'gallery_img', 'index': dash.ALL}, 'n_clicks'),
    State({'type': 'gallery_img', 'index': dash.ALL}, 'id'),
    prevent_initial_call=True
)
def handle_gallery_click(n_clicks_list, ids):
    if not n_clicks_list or all(n is None for n in n_clicks_list):
        raise dash.exceptions.PreventUpdate

    clicked_index = max(
        [(i, n) for i, n in enumerate(n_clicks_list) if n is not None],
        key=lambda x: x[1]
    )[0]
    return ids[clicked_index]['index']


@app.callback(
Output('gender_pie', 'figure'),
Input('pokemon_dropdown', 'value')
)

def update_gender_pie(pokemon_id):
    if pokemon_id is None or df.empty:
        return go.Figure()

    p = df[df["id"] == pokemon_id].iloc[0]
    gender_dist = p.get("gender_distribution", "Genderless")

    gender_labels = []
    gender_values = []
    colors = ['#3498db', '#e74c3c', '#95a5a6'] 

    if "Male" in gender_dist and "Female" in gender_dist:
        try:
            male_pct = int(gender_dist.split('%')[0])
            female_pct = 100 - male_pct
        except:
            male_pct = female_pct = 50
        gender_labels = ['Male', 'Female']
        gender_values = [male_pct, female_pct]
    elif "Male" in gender_dist:
        gender_labels = ['Male']
        gender_values = [100]
    elif "Female" in gender_dist:
        gender_labels = ['Female']
        gender_values = [100]
    else:
        gender_labels = ['Genderless']
        gender_values = [100]

    fig = go.Figure(data=[go.Pie(
        labels=gender_labels,
        values=gender_values,
        hoverinfo='label+percent',
        textinfo='label+percent',
        marker=dict(
            colors=colors[:len(gender_labels)],
            line=dict(color='white', width=2)
        ),
        pull=[0.15 if i == 0 else 0 for i in range(len(gender_labels))], 
        sort=False
    )])

    fig.update_layout(
        title="Gender Distribution",
        paper_bgcolor="#f9f9f9",
        plot_bgcolor="#f9f9f9",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig
@app.callback(
    Output('stat_histogram', 'figure'),
    Input('stat_dropdown', 'value')
)
def update_stat_histogram(selected_stat):
    if selected_stat is None or df.empty:
        return go.Figure()

    fig = go.Figure(data=[go.Histogram(
        x=df[selected_stat],
        nbinsx=20,
        marker_color='lightskyblue',
        opacity=0.75
    )])

    fig.update_layout(
        title=f'Distribution of {selected_stat.replace("-", " ").capitalize()}',
        xaxis_title=selected_stat.replace("-", " ").capitalize(),
        yaxis_title='Count',
        bargap=0.1,
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)