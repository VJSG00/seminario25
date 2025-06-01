from calculations.utils.templates import formatear_numpy
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


def graficos_tablas(resultado_final):
  
  tags_unicos = []
  datos_presentar = []

  for tag, data in resultado_final.items():
    (proy, targ, prod) = tag
    tags_unicos.append((proy, targ))

  tags_unicos = list(set(tags_unicos))
  
  #plots = {}
  #tablas = {}

  for (p_u, t_u) in tags_unicos:    #<-- combinacion (proy, targ)
    
    fig = go.Figure() #<-- Creamos un grafico
    
    dict_final = {}
    tabular_reaccion = []

    for (proy, targ, prod), data in resultado_final.items():  #<-- combinacion (proy, targ, prod)
      if (proy, targ) == (p_u, t_u):

        #------------------------------------------------------------------------------------------
        # Graficos
        A = np.array(data['Ai'].tolist() + data['Ap'].tolist())
        t_total = 20 + 72
        t_total = np.linspace(0, t_total, int(t_total) * 3)

        fig.add_trace(go.Scatter(x=t_total, y=A*1e-6, mode='lines', name=f'{data["reaction"]}'))
        
        #------------------------------------------------------------------------------------------
        # Tablas
        tabular = {
          "reaccion":(data['reaction']),
          "proyectil":data['projectile'],
          #"blanco":v['target_symbol'],
          "ratio_produccion":formatear_numpy(data['rti'],5,True),
          "ratio_total":formatear_numpy(data['rt'],5,True),
          "volumen_target":formatear_numpy(data['vtar'],4,False),
          "actividad_max":formatear_numpy(data['A_max'],5,True,conversion_power=-6),
          "nucleos_max":formatear_numpy(data['N_max'],5,True),
          "tiempo_max": formatear_numpy(data['t_max'],2,True),
          "energia_max": formatear_numpy(data['E_max'],2,True),
          #aqui añadir mas cosas.
        }
        # tablas.append(value)
        #tablas[(p_u, t_u)].append(value)
        # dict_final['tabla'] = tabular
        tabular_reaccion.append(tabular)
        #------------------------------------------------------------------------------------------

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
    dict_final['plot'] = plot_html
    dict_final['tabla'] = tabular_reaccion
    datos_presentar.append(dict_final)
    # plots.append(plot_html)
    #plots[(p_u, t_u)].append(plot_html)
    #fig.show()
    #return plot_html
  return datos_presentar