import plotly.graph_objects as go
import numpy as np

def interpolation_vs_experimental_data(secciones, energias, evaluated_data):
    """
    Grafica datos experimentales e interpolados.
    El objetivo es que se puedan comparar.
    """
  

    fig = go.Figure()

    max_energies = []

    # Graficar interpolaciones
    for i in range(len(energias)):
        max_energies.append(energias[i].max())
        fig.add_trace(go.Scatter(x=energias[i], y=secciones[i], mode='lines', name=f'DataFrame {i+1}'))

    # Graficar datos experimentales
    for df in evaluated_data:
        if len(df) > 100:
            fig.add_trace(go.Scatter(x=df['E,ev'], y=df['Sig,b'], mode='lines', line=dict(color='blue', width=1, backoff=0.1)))
        else:
            fig.add_trace(go.Scatter(x=df['E,ev'], y=df['Sig,b'], mode='markers', marker=dict(color='blue', opacity=0.2)))

    # Configurar ejes y leyenda
    fig.update_layout(
        xaxis=dict(range=[0, np.min(max_energies)]),
        xaxis_title='Energía (MeV)',
        yaxis_title='Sección Eficaz (barns)',
        title='Datos experimentales vs Interpolación cúbica de Hermite',
        showlegend=True,
        #grid=True
    )

    plot_html = fig.to_html(full_html=False )

    return plot_html

def grafico_actividad(ti, tp, Ai_dict, Ap_dict):
    fig = go.Figure()
    
    ti = np.linspace(0, ti, ti * 2)
    tp = np.linspace(0, tp, tp * 2)
    tp = ti.max() + tp
    
    # Iterate over each reaction and its activity data
    for reaction, (Ai_list, Ap_list) in zip(Ai_dict.keys(), zip(Ai_dict.values(), Ap_dict.values())):
        for Ai, Ap in zip(Ai_list, Ap_list):
            # Plot initial activity
            fig.add_trace(go.Scatter(x=ti, y=Ai, mode='lines', name=f'{reaction}'))
            # Plot post activity
            fig.add_trace(go.Scatter(x=tp, y=Ap, mode='lines', name=f'{reaction}'))
    
    # Update plot layout
    fig.update_layout(
        plot_bgcolor="white",
        xaxis_title='Tiempo',
        yaxis_title='Actividad',
        title='Actividad vs Tiempo',
        showlegend=True,
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis_gridcolor='lightgray',
        yaxis_gridcolor='lightgray',
        xaxis=dict(showline=True, linewidth=2, linecolor='lightgray'),  
        yaxis=dict(showline=True, linewidth=2, linecolor='lightgray'),  
    )

    # Optional: Export the plot to an HTML file
    plot_html = fig.to_html(full_html=False)

    return plot_html