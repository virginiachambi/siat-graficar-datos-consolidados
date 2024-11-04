from flask import Flask, render_template, request
import pandas as pd
import matplotlib
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt

matplotlib.use('Agg')
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    summary_html = None
    line_graph_url = None
    regression_graph_url = None
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip()

            df['FECHA DE LA FACTURA'] = pd.to_datetime(df['FECHA DE LA FACTURA'], errors='coerce', dayfirst=True)

            data = df.iloc[:, :4].head().to_html(classes='data', header="true", index=False)

            if 'FECHA DE LA FACTURA' in df.columns and 'IMPORTE TOTAL DE LA VENTA' in df.columns:
                df_grouped = df.groupby('FECHA DE LA FACTURA')['IMPORTE TOTAL DE LA VENTA'].sum().reset_index()
                summary = df_grouped['IMPORTE TOTAL DE LA VENTA'].describe().to_frame().T
                summary_html = summary.to_html(classes='data', header="true", index=False)

                # Gráfica de línea en memoria
                plt.figure(figsize=(10, 5))
                plt.plot(df_grouped['FECHA DE LA FACTURA'], df_grouped['IMPORTE TOTAL DE LA VENTA'], marker='o', linestyle='-', color='#FF69B4', linewidth=2, markersize=5)
                plt.title('Ventas por Día', fontsize=16, color='#D45D79')
                plt.xlabel('Fecha', fontsize=12, color='#6CA0B2')
                plt.ylabel('Importe Total de la Venta', fontsize=12, color='#6CA0B2')
                plt.xticks(rotation=45, fontsize=10)
                plt.yticks(fontsize=10)
                plt.grid(color='lightgray', linestyle='--', linewidth=0.5)
                plt.fill_between(df_grouped['FECHA DE LA FACTURA'], df_grouped['IMPORTE TOTAL DE LA VENTA'], color='#FFB6C1', alpha=0.3)
                plt.tight_layout()

                # Guardar la figura en un buffer
                line_buffer = BytesIO()
                plt.savefig(line_buffer, format='png')
                plt.close()
                line_buffer.seek(0)
                line_graph_url = base64.b64encode(line_buffer.getvalue()).decode('utf-8')

                # Gráfica de regresión lineal en memoria
                plt.figure(figsize=(10, 5))
                plt.scatter(df_grouped.index, df_grouped['IMPORTE TOTAL DE LA VENTA'], color='#FF69B4')
                m, b = np.polyfit(df_grouped.index, df_grouped['IMPORTE TOTAL DE LA VENTA'], 1)
                plt.plot(df_grouped.index, m * df_grouped.index + b, color='orange')
                plt.title('Regresión Lineal de Ventas', fontsize=16, color='#D45D79')
                plt.xlabel('Índice', fontsize=12, color='#6CA0B2')
                plt.ylabel('Importe Total de la Venta', fontsize=12, color='#6CA0B2')
                plt.xticks(fontsize=10)
                plt.yticks(fontsize=10)
                plt.tight_layout()

                # Guardar la figura en un buffer
                regression_buffer = BytesIO()
                plt.savefig(regression_buffer, format='png')
                plt.close()
                regression_buffer.seek(0)
                regression_graph_url = base64.b64encode(regression_buffer.getvalue()).decode('utf-8')

    return render_template('index.html', data=data, summary=summary_html, line_graph_url=line_graph_url, regression_graph_url=regression_graph_url)

if __name__ == '__main__':
    app.run(debug=True)
