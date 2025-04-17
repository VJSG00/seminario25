import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def grafico_secciones_experimentales(datos_experimentales: list):
    """
    TODO
    """

    
    fig = go.Figure()

    # Iterar a traves de la lista de dataframes
    for data in datos_experimentales:
        
        fig.add_trace(go.Scatter(x=np.array(data['E,ev'])*1e-6, y=data['Sig,b'], name=f'{data["reaction"]} {data["author"]}'))

    # Configurar layout

    fig.update_xaxes(minor=dict(ticklen=3, tickcolor="lightgray", showgrid=True, nticks=3),
                     minor_ticks="inside",
                     ticks="inside",
                     ticklabelstep=1,
                     mirror=True,
                     range=[0,50]
                     )
    fig.update_yaxes(ticks="inside",
                     ticklabelstep=1,
                     mirror=True,
                     range=[0,None]
                     )


    # Update plot layout
    fig.update_layout(
        width=800,
        height=500,
        autosize=False,
        plot_bgcolor="white",
        xaxis_title='Energía (MeV)',
        yaxis_title='Sección Eficaz (Barns)',
        title='Sección Eficaz Experimental vs Energía',
        showlegend=True,
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis_gridcolor='lightgray',
        yaxis_gridcolor='lightgray',
        xaxis=dict(showline=True, linewidth=2, linecolor='lightgray'),
        yaxis=dict(showline=True, linewidth=2, linecolor='lightgray'),
    )

    # Display the plot
    # fig.show()

    # # Optional: Export the plot to an HTML file
    plot_html = fig.to_html(full_html=False)
    return plot_html
