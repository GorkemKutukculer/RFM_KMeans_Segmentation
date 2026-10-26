from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('data/rfm_segments.csv')
df['Monetary'] = df['Monetary'].round(2)
if 'CustomerID' in df.columns:
    df['CustomerID'] = df['CustomerID'].astype(int).astype(str)

SEGMENT_COLORS = {
    'Champions': '#009999',
    'Potential Customers': '#2980b9',
    'At Risk VIPs': '#f39c12',
    'Lost Customers': '#c0392b'
}

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Customer Intelligence & RFM Analytics"

def create_kpi_card(title, value_id, subtitle, border_color):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted text-uppercase mb-2", style={'fontSize': '0.8rem', 'letterSpacing': '1px'}),
            html.H3(id=value_id, className="fw-bold mb-1", style={'color': '#1a252f'}),
            html.Small(subtitle, className="text-secondary", style={'fontSize': '0.75rem'})
        ]),
        className="shadow-sm border-0 mb-3",
        style={'borderLeft': f'5px solid {border_color}', 'borderRadius': '8px'}
    )

app.layout = dbc.Container(fluid=True, style={'backgroundColor': '#f4f6f9', 'minHeight': '100vh', 'padding': '0'}, children=[
    dbc.Navbar(
        dbc.Container(fluid=True, children=[
            html.Div([
                html.Span("CUSTOMER INTELLIGENCE ", style={'fontWeight': '800', 'color': '#009999', 'fontSize': '1.4rem', 'letterSpacing': '1px'}),
                html.Span("| RFM & K-Means Segmentation Suite", style={'color': '#ecf0f1', 'fontSize': '1.1rem', 'fontWeight': '300'})
            ]),
            dbc.Badge("Enterprise Analytics v1.0", color="info", className="ms-auto p-2")
        ]),
        color="#1a252f",
        dark=True,
        className="mb-4 shadow-sm py-3 px-3"
    ),

    dbc.Container(fluid=True, className="px-4", children=[
        dbc.Row([
            dbc.Col(width=12, lg=3, children=[
                dbc.Card(className="shadow-sm border-0 mb-4", style={'borderRadius': '8px'}, children=[
                    dbc.CardHeader("Control Panel & Filters", className="fw-bold text-white", style={'backgroundColor': '#1a252f'}),
                    dbc.CardBody([
                        html.Label("Select Customer Segments:", className="fw-bold mb-2 small text-uppercase text-muted"),
                        dcc.Dropdown(
                            id='segment-filter',
                            options=[{'label': seg, 'value': seg} for seg in df['Segment'].unique()],
                            value=list(df['Segment'].unique()),
                            multi=True,
                            className="mb-4"
                        ),
                        html.Label("Max Recency (Days Since Last Order):", className="fw-bold mb-2 small text-uppercase text-muted"),
                        dcc.Slider(
                            id='recency-slider',
                            min=int(df['Recency'].min()),
                            max=int(df['Recency'].max()),
                            value=int(df['Recency'].max()),
                            marks={
                                0: '0d',
                                90: '90d',
                                180: '180d',
                                int(df['Recency'].max()): f"{int(df['Recency'].max())}d"
                            },
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Hr(className="my-4"),
                        html.H6("Segment Action Playbook", className="fw-bold text-uppercase small text-muted mb-3"),
                        html.Div([
                            html.P([html.Strong("Champions: ", style={'color': '#009999'}), "Reward with loyalty programs & early product access."], className="small mb-2"),
                            html.P([html.Strong("Potential: ", style={'color': '#2980b9'}), "Offer cross-sell recommendations & threshold discounts."], className="small mb-2"),
                            html.P([html.Strong("At Risk VIPs: ", style={'color': '#f39c12'}), "Urgent personalized outreach & dedicated account support."], className="small mb-2"),
                            html.P([html.Strong("Lost: ", style={'color': '#c0392b'}), "Automated win-back email campaigns; minimize ad spend."], className="small mb-0"),
                        ])
                    ])
                ])
            ]),

            dbc.Col(width=12, lg=9, children=[
                dbc.Row([
                    dbc.Col(create_kpi_card("Active Customers", "kpi-customers", "Filtered customer base", "#009999"), width=12, md=3),
                    dbc.Col(create_kpi_card("Total Revenue", "kpi-revenue", "Gross monetary volume", "#2980b9"), width=12, md=3),
                    dbc.Col(create_kpi_card("Avg. Revenue / User", "kpi-arpu", "Customer lifetime value (ARPU)", "#f39c12"), width=12, md=3),
                    dbc.Col(create_kpi_card("Avg. Order Frequency", "kpi-frequency", "Transactions per customer", "#8e44ad"), width=12, md=3),
                ]),
                dbc.Card(className="shadow-sm border-0 mb-4", style={'borderRadius': '8px'}, children=[
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab(label="1. Executive Overview", tab_id="tab-exec", children=[
                                dbc.Row(className="mt-3", children=[
                                    dbc.Col(dcc.Graph(id='revenue-donut-chart'), width=12, lg=6),
                                    dbc.Col(dcc.Graph(id='segment-count-bar'), width=12, lg=6),
                                ]),
                                dbc.Row(className="mt-2", children=[
                                    dbc.Col(dcc.Graph(id='rfm-averages-bar'), width=12)
                                ])
                            ]),
                            dbc.Tab(label="2. 3D & 2D Cluster Space", tab_id="tab-clusters", children=[
                                dbc.Row(className="mt-3", children=[
                                    dbc.Col(dcc.Graph(id='3d-scatter-chart', style={'height': '600px'}), width=12, lg=7),
                                    dbc.Col(dcc.Graph(id='2d-scatter-chart', style={'height': '600px'}), width=12, lg=5),
                                ])
                            ]),
                            dbc.Tab(label="3. CRM Target List & Export", tab_id="tab-crm", children=[
                                html.Div(className="mt-3", children=[
                                    html.P(
                                        "Filter, sort, and export actionable customer lists directly to CSV for marketing & CRM automation.",
                                        className="text-muted small mb-3"
                                    ),
                                    dash_table.DataTable(
                                        id='crm-data-table',
                                        columns=[
                                            {"name": "Customer ID", "id": "CustomerID"},
                                            {"name": "Segment", "id": "Segment"},
                                            {"name": "Recency (Days)", "id": "Recency", "type": "numeric"},
                                            {"name": "Frequency (Orders)", "id": "Frequency", "type": "numeric"},
                                            {"name": "Monetary ($)", "id": "Monetary", "type": "numeric"},
                                        ],
                                        page_size=12,
                                        sort_action="native",
                                        filter_action="native",
                                        export_format="csv",
                                        export_headers="display",
                                        style_table={'overflowX': 'auto'},
                                        style_header={
                                            'backgroundColor': '#1a252f',
                                            'color': 'white',
                                            'fontWeight': 'bold',
                                            'textAlign': 'center'
                                        },
                                        style_cell={
                                            'textAlign': 'center',
                                            'padding': '10px',
                                            'fontFamily': 'Arial, sans-serif',
                                            'fontSize': '14px'
                                        },
                                        style_data_conditional=[
                                            {'if': {'filter_query': '{Segment} = "Champions"'}, 'backgroundColor': '#e8f8f5', 'color': '#006666', 'fontWeight': 'bold'},
                                            {'if': {'filter_query': '{Segment} = "At Risk VIPs"'}, 'backgroundColor': '#fef9e7', 'color': '#b7950b', 'fontWeight': 'bold'},
                                            {'if': {'filter_query': '{Segment} = "Lost Customers"'}, 'backgroundColor': '#fdedec', 'color': '#922b21'}
                                        ]
                                    )
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])
])

@app.callback(
    [Output('kpi-customers', 'children'),
     Output('kpi-revenue', 'children'),
     Output('kpi-arpu', 'children'),
     Output('kpi-frequency', 'children'),
     Output('revenue-donut-chart', 'figure'),
     Output('segment-count-bar', 'figure'),
     Output('rfm-averages-bar', 'figure'),
     Output('3d-scatter-chart', 'figure'),
     Output('2d-scatter-chart', 'figure'),
     Output('crm-data-table', 'data')],
    [Input('segment-filter', 'value'),
     Input('recency-slider', 'value')]
)
def update_dashboard(selected_segments, max_recency):
    if not selected_segments:
        filtered_df = df.iloc[0:0]
    else:
        filtered_df = df[(df['Segment'].isin(selected_segments)) & (df['Recency'] <= max_recency)]

    if filtered_df.empty:
        empty_fig = go.Figure().update_layout(title="No data matches selected filters", template="plotly_white")
        return "0", "$0", "$0", "0.0", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, []

    total_customers = f"{len(filtered_df):,}"
    total_revenue = f"${filtered_df['Monetary'].sum():,.0f}"
    arpu = f"${filtered_df['Monetary'].mean():,.0f}"
    avg_freq = f"{filtered_df['Frequency'].mean():.1f}x"

    rev_by_seg = filtered_df.groupby('Segment', as_index=False)['Monetary'].sum()
    fig_donut = px.pie(
        rev_by_seg, names='Segment', values='Monetary', hole=0.55,
        color='Segment', color_discrete_map=SEGMENT_COLORS,
        title="Revenue Contribution by Segment ($)"
    )
    fig_donut.update_traces(textinfo='percent+label')
    fig_donut.update_layout(template='plotly_white', showlegend=False, margin=dict(t=50, b=20, l=20, r=20))

    count_by_seg = filtered_df.groupby('Segment', as_index=False).size().rename(columns={'size': 'Customers'})
    count_by_seg = count_by_seg.sort_values('Customers', ascending=True)
    fig_bar = px.bar(
        count_by_seg, x='Customers', y='Segment', orientation='h',
        color='Segment', color_discrete_map=SEGMENT_COLORS, text='Customers',
        title="Customer Headcount per Segment"
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(template='plotly_white', showlegend=False, margin=dict(t=50, b=20, l=20, r=40))

    avg_rfm = filtered_df.groupby('Segment', as_index=False)[['Recency', 'Frequency', 'Monetary']].mean().round(1)
    fig_avg = px.bar(
        avg_rfm, x='Segment', y=['Recency', 'Frequency'], barmode='group',
        title="Average Recency (Days) vs. Frequency (Orders) by Segment",
        color_discrete_sequence=['#34495e', '#009999']
    )
    fig_avg.update_layout(template='plotly_white', yaxis_title="Average Value", margin=dict(t=50, b=20, l=20, r=20))

    fig_3d = px.scatter_3d(
        filtered_df, x='Recency', y='Frequency', z='Monetary',
        color='Segment', color_discrete_map=SEGMENT_COLORS,
        hover_data=['CustomerID'], opacity=0.75,
        title="3D RFM Spatial Cluster Distribution"
    )
    fig_3d.update_layout(template='plotly_white', margin=dict(t=50, b=10, l=10, r=10))

    fig_2d = px.scatter(
        filtered_df, x='Frequency', y='Monetary',
        color='Segment', color_discrete_map=SEGMENT_COLORS,
        hover_data=['CustomerID', 'Recency'],
        log_x=True, log_y=True, opacity=0.7,
        title="2D Behavioral Map (Log Scale: Frequency vs. Monetary)"
    )
    fig_2d.update_layout(template='plotly_white', margin=dict(t=50, b=20, l=20, r=20))

    table_data = filtered_df.sort_values(by='Monetary', ascending=False).to_dict('records')

    return total_customers, total_revenue, arpu, avg_freq, fig_donut, fig_bar, fig_avg, fig_3d, fig_2d, table_data

if __name__ == '__main__':
    app.run(debug=True)