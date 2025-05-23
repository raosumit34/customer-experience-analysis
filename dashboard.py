import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Read the dataset
df = pd.read_csv('customer_experience_data.csv')

# Initialize the Dash app with a more user-friendly theme (e.g., LUX)
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY]) # Changed from PULSE to MINTY

# --- Prepare Initial Figures ---
# This is done upfront so they can be directly assigned in the layout.

# Initial figure for Location Analysis
initial_grouped_df = df.groupby('Location', as_index=False).agg(
    Avg_Satisfaction_Score=('Satisfaction_Score', 'mean'),
    Avg_Feedback_Score=('Feedback_Score', 'mean')
)
initial_melted_df = initial_grouped_df.melt(
    id_vars='Location',
    value_vars=['Avg_Satisfaction_Score', 'Avg_Feedback_Score'],
    var_name='Metric',
    value_name='Average_Score'
)
initial_location_analysis_fig = px.bar(
    initial_melted_df,
    x='Location',
    y='Average_Score',
    color='Metric',
    barmode='group',
    title='Location Performance: Satisfaction & Feedback', # More descriptive title
    color_discrete_sequence=["#636EFA", "#EF553B"] # Vibrant colors for metrics
)
initial_location_analysis_fig.update_layout(template="plotly_white", title_x=0.5)

# Initial figure for Satisfaction Distribution
initial_satisfaction_fig = px.pie(df,
                                 values='Satisfaction_Score',
                                 names='Satisfaction_Score',
                                 title='Customer Satisfaction Snapshot', # More descriptive title
                                 hole=0.4, # Increased hole size for donut chart
                                 color_discrete_sequence=px.colors.sequential.Plasma_r) # Vibrant color sequence
initial_satisfaction_fig.update_traces(textinfo='percent+label')
initial_satisfaction_fig.update_layout(template="plotly_white", title_x=0.5)

# Initial figure for Age vs Satisfaction
initial_age_satisfaction_fig = px.scatter_3d(df,
                                           x='Age',
                                           y='Satisfaction_Score',
                                           z='Time_Spent_on_Site',
                                           color='Retention_Status',
                                           title='3D Insight: Age, Satisfaction & Site Engagement', # More descriptive title
                                           color_discrete_map={'Retained': '#00A0B0', 'Churned': '#FF6F61'}, # Updated colors
                                           symbol='Retention_Status', # Different symbols for status
                                           opacity=0.8) # Set opacity directly
initial_age_satisfaction_fig.update_traces(marker=dict(size=5,
                                                       opacity=0.8, # Ensured opacity is here for consistency
                                                       line=dict(width=0.5, color='DarkSlateGrey'))) # Configure marker size and line
initial_age_satisfaction_fig.update_layout(template="plotly_white", title_x=0.5)

# Initial figure for Products Analysis
initial_products_analysis_fig = px.scatter(df,
                                         x='Products_Purchased',
                                         y='Products_Viewed',
                                         size='Time_Spent_on_Site',
                                         color='Retention_Status',
                                         animation_frame='Satisfaction_Score',
                                         title='Animated: Product Interaction Dynamics & Retention', # More descriptive title
                                         color_discrete_map={'Retained': '#6B5B95', 'Churned': '#FFC408'}) # Updated colors
initial_products_analysis_fig.update_layout(template="plotly_white", title_x=0.5)


# --- App Layout ---
# Styling for H1 and P tags, letting the PULSE theme handle background
app.layout = html.Div(children=[
    html.H1("Interactive Customer Experience Dashboard",
            style={'textAlign': 'center', 'marginBottom': '10px', 'marginTop': '20px', 'fontWeight': 'bold', 'color': '#4A148C'}), # Adjusted H1 style, added color
    html.P("Explore customer data to understand satisfaction, behavior, and retention. Use the filters below to customize your view.",
           style={'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '1.15em', 'color': '#004D40'}), # Adjusted P style, added color

    # Filters Section - Placed at the top for better usability
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([ # Wrap filters in a card
                html.H3("Customize Your Data View", style={'marginTop': '10px', 'marginBottom': '25px', 'textAlign': 'center', 'color': '#D32F2F'}), # Added color
                html.Div([
                    html.Label("Filter by Age Range:", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.RangeSlider(
                        id='age-range',
                        min=df['Age'].min(),
                        max=df['Age'].max(),
                        value=[df['Age'].min(), df['Age'].max()],
                        marks={str(age): f"{age}" for age in range(int(df['Age'].min()), int(df['Age'].max()) + 1, 10)},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], style={'marginBottom': '30px'}), 
                html.Div([
                    html.Label("Filter by Customer Location:", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='location-filter',
                        options=[{'label': loc, 'value': loc} for loc in df['Location'].unique()],
                        value=df['Location'].unique(),
                        multi=True,
                        placeholder="Select one or more locations"
                    )
                ])
            ]))
        ], width=12) 
    ], className="mb-5"),

    # Charts Section
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([ # Wrap graph in Card
                dcc.Graph(id='satisfaction-dist', figure=initial_satisfaction_fig),
                html.P("Distribution of customer satisfaction scores.",
                       style={'textAlign': 'center', 'fontSize': '0.9em', 'marginTop': '10px'})
            ]))
        ], width=6, className="mb-4"),
        dbc.Col([
            dbc.Card(dbc.CardBody([ # Wrap graph in Card
                dcc.Graph(id='age-satisfaction', figure=initial_age_satisfaction_fig),
                html.P("3D view: Age, Satisfaction, Site Time, and Retention.",
                       style={'textAlign': 'center', 'fontSize': '0.9em', 'marginTop': '10px'})
            ]))
        ], width=6, className="mb-4")
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([ # Wrap graph in Card
                dcc.Graph(id='location-analysis', figure=initial_location_analysis_fig),
                html.P("Average scores by customer location.",
                       style={'textAlign': 'center', 'fontSize': '0.9em', 'marginTop': '10px'})
            ]))
        ], width=6, className="mb-4"),
        dbc.Col([
            dbc.Card(dbc.CardBody([ # Wrap graph in Card
                dcc.Graph(id='products-analysis', figure=initial_products_analysis_fig),
                html.P("Product interaction animated by satisfaction score.",
                       style={'textAlign': 'center', 'fontSize': '0.9em', 'marginTop': '10px'})
            ]))
        ], width=6, className="mb-4")
    ])
])


# Callback to update visualizations based on filters
@app.callback(
    [Output('satisfaction-dist', 'figure'),
     Output('age-satisfaction', 'figure'),
     Output('location-analysis', 'figure'),
     Output('products-analysis', 'figure')],
    [Input('age-range', 'value'),
     Input('location-filter', 'value')]
)
def update_graphs(age_range, locations):
    filtered_df = df[
        (df['Age'] >= age_range[0]) &
        (df['Age'] <= age_range[1]) &
        (df['Location'].isin(locations))
    ]
    
    # Update all visualizations with filtered data and new titles/templates
    satisfaction_dist_fig = px.pie(filtered_df, 
                             values='Satisfaction_Score',
                             names='Satisfaction_Score',
                             title='Customer Satisfaction Snapshot', 
                             hole=0.4, # Consistent hole size
                             color_discrete_sequence=px.colors.sequential.Plasma_r) # Consistent colors
    satisfaction_dist_fig.update_traces(textinfo='percent+label')
    satisfaction_dist_fig.update_layout(template="plotly_white", title_x=0.5)
    
    age_satisfaction_fig = px.scatter_3d(filtered_df,
                                   x='Age',
                                   y='Satisfaction_Score',
                                   z='Time_Spent_on_Site',
                                   color='Retention_Status',
                                   title='3D Insight: Age, Satisfaction & Site Engagement', 
                                   color_discrete_map={'Retained': '#00A0B0', 'Churned': '#FF6F61'}, # Updated colors
                                   symbol='Retention_Status', # Consistent symbols
                                   opacity=0.8) # Set opacity directly
    age_satisfaction_fig.update_traces(marker=dict(size=5,
                                                 opacity=0.8, # Ensure opacity is set for markers
                                                 line=dict(width=0.5, color='DarkSlateGrey'))) # Configure marker properties via update_traces
    age_satisfaction_fig.update_layout(template="plotly_white", title_x=0.5)
    
    # Prepare data for grouped bar chart
    grouped_location_df = filtered_df.groupby('Location', as_index=False).agg(
        Avg_Satisfaction_Score=('Satisfaction_Score', 'mean'),
        Avg_Feedback_Score=('Feedback_Score', 'mean')
    )
    melted_location_df = grouped_location_df.melt(
        id_vars='Location',
        value_vars=['Avg_Satisfaction_Score', 'Avg_Feedback_Score'],
        var_name='Metric',
        value_name='Average_Score'
    )
    location_analysis_fig = px.bar(
        melted_location_df,
        x='Location',
        y='Average_Score',
        color='Metric',
        barmode='group',
        title='Location Performance: Satisfaction & Feedback',
        color_discrete_sequence=["#636EFA", "#EF553B"] # Consistent colors
    )
    location_analysis_fig.update_layout(template="plotly_white", title_x=0.5)
    
    products_analysis_fig = px.scatter(filtered_df,
                                 x='Products_Purchased',
                                 y='Products_Viewed',
                                 size='Time_Spent_on_Site',
                                 color='Retention_Status',
                                 animation_frame='Satisfaction_Score',
                                 title='Animated: Product Interaction Dynamics & Retention',
                                 color_discrete_map={'Retained': '#6B5B95', 'Churned': '#FFC408'}) # Updated colors
    products_analysis_fig.update_layout(template="plotly_white", title_x=0.5)
    
    return satisfaction_dist_fig, age_satisfaction_fig, location_analysis_fig, products_analysis_fig

if __name__ == '__main__':
    app.run(debug=True)