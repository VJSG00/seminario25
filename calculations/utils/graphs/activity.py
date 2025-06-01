import plotly.graph_objects as go
import numpy as np

def grafico_actividad_producto(resultado_final, ti, tp):
  """
  TODO
  """
  
  ti = np.linspace(0, ti, ti * 2)
  tp = np.linspace(0, tp, tp * 2)
  tp = ti.max() + tp
  t_total = ti.tolist() + tp.tolist()

  fig = go.Figure()

  for tag, data in resultado_final.items():
    
    A = np.array(data['Ai'].tolist() + data['Ap'].tolist())
    
    reaction = data['reaction']
    fig.add_trace(go.Scatter(x=t_total, y=A*1e-6, mode='lines', name=f'{reaction}'))
  
  
    # Personalizar ejes.
  fig.update_xaxes(minor=dict(ticklen=3, tickcolor="lightgray", showgrid=True, nticks=3),
                    minor_ticks="inside",
                    ticks="inside",
                    ticklabelstep=1,
                    mirror=True,
                    range=[0,None]
                    )
  fig.update_yaxes(ticks="inside",
                    ticklabelstep=1,
                    mirror=True,
                    range=[0,None]
                    )


  # Update plot layout
  fig.update_layout(
      width=800,
      height=600,
      autosize=False,
      plot_bgcolor="white",
      xaxis_title='Tiempo (h)',
      yaxis_title='Actividad (MBq)',
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
  #fig.show()
  return plot_html

def grafico_actividad_simplificado(resultado_final):
  """
  TODO
  """
  
  # ti = np.linspace(0, ti, ti * 2)
  # tp = np.linspace(0, tp, tp * 2)
  # tp = ti.max() + tp
  # t_total = ti.tolist() + tp.tolist()

  fig = go.Figure()

  for tag, data in resultado_final.items():
    
    A = np.array(data['Ai'].tolist() + data['Ap'].tolist())
    reaction = data['reaction']
    t_total = data['t_max'] + 72
    t_total = np.linspace(0, t_total, int(t_total) * 3)
    
    fig.add_trace(go.Scatter(x=t_total, y=A*1e-6, mode='lines', name=f'{reaction}'))
  
  
    # Personalizar ejes.
  fig.update_xaxes(minor=dict(ticklen=3, tickcolor="lightgray", showgrid=True, nticks=3),
                    minor_ticks="inside",
                    ticks="inside",
                    ticklabelstep=1,
                    mirror=True,
                    range=[0,None]
                    )
  fig.update_yaxes(ticks="inside",
                    ticklabelstep=1,
                    mirror=True,
                    range=[0,None]
                    )


  # Update plot layout
  fig.update_layout(
      width=800,
      height=600,
      autosize=False,
      plot_bgcolor="white",
      xaxis_title='Tiempo (h)',
      yaxis_title='Actividad (MBq)',
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
  #fig.show()
  return plot_html