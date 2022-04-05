#https://plotly.com/python/builtin-colorscales/
#https://dash.plotly.com/interactive-graphing
#https://community.plotly.com/t/remove-all-traces/13469
#https://dash.plotly.com/cytoscape/responsive

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

from db.conn import open_conn

selected_bairro = 'TODOS'
selected_us = 'TODOS'

token = 'pk.eyJ1IjoidHh1YmEiLCJhIjoiY2t5Nm11bTA3MHducDJ2cWlvZ2hlcnRoZiJ9.w_FznIHHX3iLK677espFUg'

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
div_padding = 10

df_geojson_curitiba = pd.read_csv('data/geojson_curitiba_inicial.csv', index_col=0).reset_index()
df_geojson_curitiba['vazio'] = 0

f = open('data/geojson_curitiba.json') 
geojson_curitiba = json.load(f)

df_geojson_unidades_saude = pd.read_csv('data/geojson_unidades_saude_inicial.csv', index_col=0).reset_index()

f = open('data/geojson_unidades_saude.json') 
geojson_unidades_saude = json.load(f)

conn = open_conn()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H2("PROTÓTIPO DE DASHBOARD PARA VISUALIZAÇÃO DE DESLOCAMENTO DE PACIENTES POR CURITIBA"), 
                
                html.Div([
                    html.Label('Bairro de Origem', style=dict(width='40%')),
                    dcc.Dropdown(
                        id='dropdown-bairro',
                        options=[{'value': x, 'label': x} 
                            for x in ['TODOS'] + list(df_geojson_curitiba['nome'])],
                        value='TODOS',
                        style=dict(width='100%'),
                        clearable=False
                    ),
                ], style={'display': 'flex', 'flex-direction': 'row','padding': 0, 'flex': 1}),
    
                html.Div([
                    html.Label('US/UPA Destino', style=dict(width='40%')),
                    dcc.Dropdown(
                        id='dropdown-unidade-saude',
                        options=[{'value': x, 'label': x} 
                            for x in ['TODOS'] + list(df_geojson_unidades_saude['nome'])],
                        value='TODOS',
                        style=dict(width='100%'),
                        clearable=False
                    ),
                ], style={'display': 'flex', 'flex-direction': 'row','padding': 0, 'flex': 1}),

                html.Div([
                    html.Label('Ano', style=dict(width='40%')),
                    dcc.Dropdown(
                        id='dropdown-ano',
                        options=[{'value': x, 'label': x} 
                            for x in ['TODOS','2016','2017','2018','2019']],
                        value='TODOS',
                        style=dict(width='100%'),
                        clearable=False
                    ),
                ], style={'display': 'flex', 'flex-direction': 'row','padding': 0, 'flex': 1}),
                # html.Div([
                #     dcc.Markdown("""
                #         **Click Data**

                #         Click on points in the graph.
                #     """),
                #     html.Pre(id='click-data', style=styles['pre']),
                # ], className='three columns'),
            ], style={'display': 'flex', 'flex-direction': 'column','padding': div_padding, 'flex': 1}),
            html.Div([
                html.Div([
                    dcc.Graph(id='grafico-sexo', 
                        figure=dict(layout=dict(autosize=True)),
                        config=dict(responsive=True, displayModeBar=False),
                        style=dict(height='100%', width='100%'),
                    )
                ], style={'padding': div_padding, 'flex': 1}),
                html.Div([
                    dcc.Graph(id='grafico-idade', 
                        figure=dict(layout=dict(autosize=True)),
                        config=dict(responsive=True, displayModeBar=False),
                        style=dict(height='100%', width='100%'),
                    )
                ], style={'padding': div_padding, 'flex': 1}),
            ], style={'display': 'flex', 'flex-direction': 'row','flex': 1}),
            html.Div([
                dcc.Graph(id='grafico-cid', 
                    figure=dict(layout=dict(autosize=True)),
                    config=dict(responsive=True, displayModeBar=False),
                    style=dict(height='100%', width='100%'),
                )
            ], style={'padding': div_padding, 'flex': 1}),
            html.Div([
                dcc.Graph(id='grafico-mes',
                    figure=dict(layout=dict(autosize=True)),
                    config=dict(responsive=True, displayModeBar=False),
                    style=dict(height='100%', width='100%'),
                )
            ], style={'padding': div_padding, 'flex': 1}),
        ], style={'display': 'flex', 'flex-direction': 'column', 'height': '95vh'})
    ], style={'padding': 0, 'flex': 1}),
    html.Div([
        dcc.Graph(id="mapa",
            figure=dict(layout=dict(autosize=True)),
            config=dict(responsive=True, displayModeBar=False),
            style=dict(height='100%', width='100%'),
        ),
    ], style={'padding': 0, 'flex': 2}),
    # https://dash.plotly.com/sharing-data-between-callbacks
    # dcc.Store stores the intermediate value
    dcc.Store(id='intermediate-value')
], style={'display': 'flex', 'flex-direction': 'row', 'height': '95vh'},)

# @app.callback(
#     Output('intermediate-value', 'data'),
#     Input("dropdown-bairro", "value"),
#     Input("dropdown-unidade-saude", "value"))
# def redundancia_bairro(bairro, unidade_saude):
#     if(bairro == None):
#         selected_bairro = 'TODOS'
    
#     if(unidade_saude == None):
#         selected_us = 'TODOS'
#     # https://dash.plotly.com/sharing-data-between-callbacks
#     return json.dumps({})


@app.callback(
    # Output('click-data', 'children'),
    Output("dropdown-bairro", "value"),
    Output("dropdown-unidade-saude", "value"),
    Input('mapa', 'clickData'))
def display_click_data(clickData):
    global selected_bairro
    global selected_us

    if clickData == None:
        clickData = 'sem cliques'
        return selected_bairro, selected_us

    elif clickData['points'][0]['curveNumber'] == 0:
        selected_bairro = clickData['points'][0]['location']
        return selected_bairro, selected_us
    
    else:
        selected_us = clickData['points'][0]['text']
        return selected_bairro, selected_us

@app.callback(
    Output("mapa", "figure"), 
    [Input("dropdown-bairro", "value"),
    Input("dropdown-unidade-saude", "value"), 
    Input("dropdown-ano", "value")])
def display_mapa_choropleth(bairro, unidade_saude, ano):
    global selected_bairro
    global selected_us

    #arrumar incongruencia de valores
    if bairro == None:
        bairro = 'TODOS'
        selected_bairro = 'TODOS'

    if unidade_saude == None:
        unidade_saude = 'TODOS'
        selected_us = 'TODOS'

    if ano == None:
        ano = 'TODOS'

    #visualização da cor dos bairros no grafico
    df_geojson_curitiba.vazio = 0

    if(bairro != 'TODOS'):
        df_geojson_curitiba.loc[df_geojson_curitiba['nome'] == bairro, 'vazio'] = 10000

    #criação efetiva do mapa
    fig = px.choropleth_mapbox(
        df_geojson_curitiba, 
        geojson=geojson_curitiba, 
        color='vazio',
        color_continuous_scale='Blues',
        locations="nome", 
        featureidkey="properties.nome",
        center={"lat": -25.492, "lon": -49.2937}, 
        zoom=10.5,
        range_color=[0, 6500],
        hover_name = 'nome',
        hover_data = {'index':False,'nome':False, 'geojson':False, 'centroid':False, 'vazio':False})

    #token de acesso para uso do mapa
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_accesstoken=token)

    

    #se tiver unidade de saude E bairro selecionado
    if(unidade_saude != 'TODOS' and bairro != 'TODOS'):
        centroide_bairro = df_geojson_curitiba[df_geojson_curitiba['nome'] == bairro]
        longitude_centroide = [json.loads(item)['coordinates'][0] for item in centroide_bairro['centroid']]
        latitude_centroide = [json.loads(item)['coordinates'][1] for item in centroide_bairro['centroid']]
        
        df_unidade_selecionada = df_geojson_unidades_saude[df_geojson_unidades_saude['nome']==unidade_saude].reset_index(drop=True)
        lons = [json.loads(item)['coordinates'][0] for item in df_unidade_selecionada['geojson']]
        lats = [json.loads(item)['coordinates'][1] for item in df_unidade_selecionada['geojson']]

        #linha para centroide
        fig.add_trace(go.Scattermapbox(
            mode = "lines",
            lon = [lons[0], longitude_centroide[0]],
            lat = [lats[0], latitude_centroide[0]],
            marker = {'size': 0},
            text=['',''],
            line_color='rgb(0, 0, 255)',
            name='',
            hovertemplate='%{text}'
            )
        )

    #se tiver o bairro selecionado mas a us nao
    if(unidade_saude == 'TODOS' and bairro != 'TODOS'):
        df = pd.read_sql('''
            select distinct desc_unidade 
            from marcelo_mv_count_geral
            where bairro = \'''' + bairro + '''\'
            and (cast(ano as varchar) = \'''' + str(ano) + '''\'
                or \'''' + str(ano) + '''\' = 'TODOS')
        ''', conn)

        df_unidades = df_geojson_unidades_saude.merge(df, left_on='nome', right_on='desc_unidade')
        lons = [json.loads(item)['coordinates'][0] for item in df_unidades['geojson']]
        lats = [json.loads(item)['coordinates'][1] for item in df_unidades['geojson']]

        centroide_bairro = df_geojson_curitiba[df_geojson_curitiba['nome'] == bairro]
        longitude_centroide = [json.loads(item)['coordinates'][0] for item in centroide_bairro['centroid']]
        latitude_centroide = [json.loads(item)['coordinates'][1] for item in centroide_bairro['centroid']]
        
        for i in range(len(df_unidades)):
            #linha para centroide
            fig.add_trace(go.Scattermapbox(
                mode = "lines",
                lon = [lons[i], longitude_centroide[0]],
                lat = [lats[i], latitude_centroide[0]],
                marker = {'size': 0},
                text=['',''],
                line_color='rgb(0, 0, 255)',
                name='',
                hovertemplate='%{text}'
                )
            )
        
    #se tiver a us selecionada mas o bairro nao
    if(unidade_saude != 'TODOS' and bairro == 'TODOS'):
        df = pd.read_sql('''
            select distinct bairro 
            from marcelo_mv_count_geral
            where desc_unidade = \'''' + unidade_saude + '''\'
            and (cast(ano as varchar) = \'''' + str(ano) + '''\'
                or \'''' + str(ano) + '''\' = 'TODOS')
        ''', conn)

        df_unidades = df_geojson_unidades_saude[df_geojson_unidades_saude['nome'] == unidade_saude]
        lons = [json.loads(item)['coordinates'][0] for item in df_unidades['geojson']]
        lats = [json.loads(item)['coordinates'][1] for item in df_unidades['geojson']]

        centroide_bairro = df_geojson_curitiba.merge(df, left_on='nome', right_on='bairro')
        longitude_centroide = [json.loads(item)['coordinates'][0] for item in centroide_bairro['centroid']]
        latitude_centroide = [json.loads(item)['coordinates'][1] for item in centroide_bairro['centroid']]
        
        for i in range(len(centroide_bairro)):
            #linha para centroide
            fig.add_trace(go.Scattermapbox(
                mode = "lines",
                lon = [lons[0], longitude_centroide[i]],
                lat = [lats[0], latitude_centroide[i]],
                marker = {'size': 0},
                text=['',''],
                line_color='rgb(0, 0, 255)',
                name='',
                hovertemplate='%{text}'
                )
            )

    #todas as US e seus pontos - com regulação de tamanho

    df = pd.read_sql('''
            select sum(nmr) as nmr, desc_unidade 
            from marcelo_mv_count_geral
            where bairro = \'''' + bairro + '''\'
                or \'''' + bairro + '''\' = 'TODOS'
            and (cast(ano as varchar) = \'''' + str(ano) + '''\'
                or \'''' + str(ano) + '''\' = 'TODOS')
            group by ano, desc_unidade
        ''', conn)

    df['size'] = 5 + 10 * (df['nmr']/df['nmr'].max())

    df_unidades = df_geojson_unidades_saude.merge(df, left_on='nome', right_on='desc_unidade')
    lons = [json.loads(item)['coordinates'][0] for item in df_unidades['geojson']]
    lats = [json.loads(item)['coordinates'][1] for item in df_unidades['geojson']]
    texts = [item for item in df_unidades['nome']]
    size = [item for item in df_unidades['size']]

    # lons = [item['geometry']['coordinates'][0] for item in geojson_unidades_saude['features']]
    # lats = [item['geometry']['coordinates'][1] for item in geojson_unidades_saude['features']]
    # texts = [item['properties']['nome'] for item in geojson_unidades_saude['features']]

    fig.add_scattermapbox(
        lat = lats,
        lon = lons,
        mode = 'markers',
        text = texts,
        marker_size=size,
        marker_color='rgb(235, 0, 100)',
        name='',
        hovertemplate='%{text}'
    )

    #se tiver unidade de saude selecionada    
    if(unidade_saude != 'TODOS'):
        df_unidade_selecionada = df_geojson_unidades_saude[df_geojson_unidades_saude['nome']==unidade_saude].reset_index(drop=True)
        lons = [json.loads(item)['coordinates'][0] for item in df_unidade_selecionada['geojson']]
        lats = [json.loads(item)['coordinates'][1] for item in df_unidade_selecionada['geojson']]
        texts = [item for item in df_unidade_selecionada['nome']]

        #marker azulao
        fig.add_scattermapbox(
            lat = lats,
            lon = lons,
            mode = 'markers',
            text = texts,
            marker_size=20,
            marker_color='rgb(0, 0, 255)',
            name='',
            hovertemplate='%{text}'
        )


    
    
    fig.update_layout(showlegend=False)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_yaxes(automargin=True)


    return fig

@app.callback(
    Output("grafico-sexo", "figure"), 
    [Input("dropdown-bairro", "value"),
    Input("dropdown-unidade-saude", "value"), 
    Input("dropdown-ano", "value")])
def display_grafico_sexo(bairro, unidade_saude, ano):
    global selected_bairro
    global selected_us
    
    if bairro == None:
        bairro = 'TODOS'
        selected_bairro = 'TODOS'

    if unidade_saude == None:
        unidade_saude = 'TODOS'
        selected_us = 'TODOS'

    if ano == None:
        ano = 'TODOS'

    df = pd.read_sql('''
        select sum(nmr) as atendimentos, sexo 
        from marcelo_mv_filtros_sexo
        where (bairro = \''''+bairro+'''\'
            or \''''+bairro+'''\' = 'TODOS')
            and (desc_unidade = \''''+unidade_saude+'''\'
            or \''''+unidade_saude+'''\' = 'TODOS')
            and (cast(ano as varchar) = \''''+ano+'''\'
            or \''''+ano+'''\' = 'TODOS')
        group by sexo
    ''', conn)

    fig = px.pie(df, values='atendimentos', names='sexo', color='sexo', title='',
        color_discrete_map={'F':'#FF007F', 'M':'blue'})
    
    fig.update_layout(
        margin={"r":5,"t":5,"l":5,"b":5},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')

    return fig

@app.callback(
    Output("grafico-mes", "figure"),
    [Input("dropdown-bairro", "value"),
    Input("dropdown-unidade-saude", "value"), 
    Input("dropdown-ano", "value")])
def display_grafico_mes(bairro, unidade_saude, ano):
    global selected_bairro
    global selected_us
        
    if bairro == None:
        bairro = 'TODOS'
        selected_bairro = 'TODOS'

    if unidade_saude == None:
        unidade_saude = 'TODOS'
        selected_us = 'TODOS'

    if ano == None:
        ano = 'TODOS'

    df = pd.read_sql('''
        select sum(nmr) as atendimentos, mes 
        from marcelo_mv_filtros_mes
        where (bairro = \''''+bairro+'''\'
            or \''''+bairro+'''\' = 'TODOS')
            and (desc_unidade = \''''+unidade_saude+'''\'
            or \''''+unidade_saude+'''\' = 'TODOS')
            and (cast(ano as varchar) = \''''+ano+'''\'
            or \''''+ano+'''\' = 'TODOS')
        group by mes, mes_nmr
        order by mes_nmr
    ''', conn)

    fig = px.bar(df, y='atendimentos', x='mes', title='')
    
    fig.update_layout(
        margin={"r":5,"t":5,"l":5,"b":5},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    
    return fig

@app.callback(
    Output("grafico-idade", "figure"),
    [Input("dropdown-bairro", "value"),
    Input("dropdown-unidade-saude", "value"), 
    Input("dropdown-ano", "value")])
def display_grafico_idade(bairro, unidade_saude, ano):
    global selected_bairro
    global selected_us
        
    if bairro == None:
        bairro = 'TODOS'
        selected_bairro = 'TODOS'

    if unidade_saude == None:
        unidade_saude = 'TODOS'
        selected_us = 'TODOS'

    if ano == None:
        ano = 'TODOS'

    df = pd.read_sql('''
        select sum(nmr) as atendimentos, idade 
        from marcelo_mv_filtros_idade
        where (bairro = \''''+bairro+'''\'
            or \''''+bairro+'''\' = 'TODOS')
            and (desc_unidade = \''''+unidade_saude+'''\'
            or \''''+unidade_saude+'''\' = 'TODOS')
            and (cast(ano as varchar) = \''''+ano+'''\'
            or \''''+ano+'''\' = 'TODOS')
        group by idade
        order by idade
    ''', conn)

    fig = px.bar(df, y='atendimentos', x='idade', title='')
    
    fig.update_layout(
        margin={"r":5,"t":5,"l":5,"b":5},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    
    return fig

@app.callback(
    Output("grafico-cid", "figure"),
    [Input("dropdown-bairro", "value"),
    Input("dropdown-unidade-saude", "value"), 
    Input("dropdown-ano", "value")])
def display_grafico_cid(bairro, unidade_saude, ano):
    global selected_bairro
    global selected_us
        
    if bairro == None:
        bairro = 'TODOS'
        selected_bairro = 'TODOS'

    if unidade_saude == None:
        unidade_saude = 'TODOS'
        selected_us = 'TODOS'

    if ano == None:
        ano = 'TODOS'

    df = pd.read_sql('''
        select * from (
            select sum(nmr) as atendimentos, concat(left(desc_cid, 10),'...') as doença, desc_cid
            from marcelo_mv_filtros_cid
            where (bairro = \''''+bairro+'''\'
                or \''''+bairro+'''\' = 'TODOS')
                and (desc_unidade = \''''+unidade_saude+'''\'
                or \''''+unidade_saude+'''\' = 'TODOS')
                and (cast(ano as varchar) = \''''+ano+'''\'
                or \''''+ano+'''\' = 'TODOS')
            group by desc_cid
            order by atendimentos desc
            limit 5
        )t order by atendimentos
    ''', conn)

    fig = px.bar(df, y='doença', x='atendimentos', title='', custom_data=['desc_cid'], orientation='h')
    
    fig.update_traces(
        hovertemplate='''doença=%{customdata[0]}
            <br>atendimentos=%{x}'''
    )

    fig.update_layout(
        margin={"r":5,"t":5,"l":5,"b":5},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    
    return fig

app.run_server(debug=True)#, dev_tools_hot_reload=True)

# ideia geral: 
# colocar o mapa à direita
# à esquerda separar entre cima e baixo 
# acima colocar o painel de controle
# abaixo colocar as estatísticas

# o painel de controle
# esta seção contém primeiramente o modo de calor do mapa
# em segundo lugar duas dropdowns contendo o bairro e a UPA
# em terceiro lugar os filtros

# as estatisticas
# conterão gráficos de barra representando as estatísticas
# estatisticas atualizadas quando o painel de controle muda

# o mapa:
# ao clicar no mapa em um distrito ativa a dropdown de bairro, o mesmo para upa
# ao selecionar um bairro e uma upa traça uma linha entre elas 
