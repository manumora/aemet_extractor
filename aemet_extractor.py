import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin

output_dir = "/var/www/html/"
#output_dir = "./"

os.makedirs(output_dir, exist_ok=True)

def extraer_contenido_aemet():
    """
    Extract content from the 'contenedor_central_izq' div of the AEMET page for Mérida
    """
    url = "https://www.aemet.es/es/eltiempo/prediccion/municipios/merida-id06083"
    
    try:
        # Perform the HTTP request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the contenedor_central_izq div
        contenedor = soup.find('div', class_='contenedor_central_izq')
        
        if not contenedor:
            print("Could not find the 'contenedor_central_izq' div")
            return None
        
        # Remove unwanted elements
        elementos_a_eliminar = [
            contenedor.find('div', class_='notas_tabla'),
            contenedor.find('div', class_='alinear_texto_dcha'),
            contenedor.find('div', class_='enlace_mas_detalle margintop5px_important'),
            contenedor.find('div', class_='paddingbot40')
        ]
        
        for elemento in elementos_a_eliminar:
            if elemento:
                elemento.decompose()
        
        # Eliminar filas con clase ocultar_filas_tabla
        filas_ocultas = contenedor.find_all('tr', class_='ocultar_filas_tabla')
        for fila in filas_ocultas:
            fila.decompose()
        
        # Add title above the table
        titulo = soup.new_tag('h1')
        titulo['style'] = 'text-align: center; margin: 20px 0; color: #1b4990;'
        titulo.string = 'Predicción metereológica - Mérida'
        
        # Find the table to insert the title before it
        tabla_prediccion = contenedor.find('table', id='tabla_prediccion')
        if tabla_prediccion:
            contenedor_tabla = tabla_prediccion.parent
            contenedor_tabla.insert(0, titulo)
        else:
            # If we don't find the table, insert at the beginning of the container
            contenedor.insert(0, titulo)
        
        # Extract all CSS code
        estilos = ""
        for style_tag in soup.find_all('style'):
            estilos += style_tag.string + "\n"
        
        # Also extract links to external stylesheets
        css_links = []
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css_href = link.get('href')
                if not css_href.startswith('http'):
                    css_href = urljoin(url, css_href)
                css_links.append(css_href)
        
        # Convert image paths to absolute URLs
        for img in contenedor.find_all('img'):
            if img.get('src'):
                src = img['src']
                if not src.startswith('http'):
                    img['src'] = urljoin(url, src)
        
        # Find any relative URLs in CSS styles and convert them to absolute URLs
        pattern = r'url\([\'"]?([^\'")]+)[\'"]?\)'
        def replace_url(match):
            path = match.group(1)
            if not path.startswith('http') and not path.startswith('data:'):
                return f'url("{urljoin(url, path)}")'
            return match.group(0)
        
        estilos = re.sub(pattern, replace_url, estilos)
        
        # Convert paths in href attributes to absolute URLs
        for a in contenedor.find_all('a'):
            if a.get('href'):
                href = a['href']
                if not href.startswith('http') and not href.startswith('#') and not href.startswith('javascript:'):
                    a['href'] = urljoin(url, href)
        
        # Generate the HTML
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predicción meteorológica para Mérida - AEMET</title>
    <style>
{estilos}

/* Estilos para aplicar zoom al 150% */
body {{
    transform: scale(1.7);
    transform-origin: top left;
    width: 58.82%; /* 100/1.7 = 58.82% para compensar el zoom */
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    background-image: url('https://raw.githubusercontent.com/manumora/aemet_extractor/refs/heads/master/background.png');
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-size: cover;
}}

/* Ajustes adicionales para mejorar la visualización con el zoom */
html {{
    overflow-x: hidden;
}}

table, img {{
    max-width: 100%;
}}

/* Estilo para aplicar fondo blanco a las celdas de la tabla */
td {{
    background-color: white !important;
}}
    </style>
    
    {' '.join([f'<link rel="stylesheet" href="{css}">' for css in css_links])}
</head>
<body>
    {contenedor}
    
    <script>
        // Disable links to prevent navigation outside the page
        document.addEventListener('DOMContentLoaded', function() {{
            var enlaces = document.getElementsByTagName('a');
            for (var i = 0; i < enlaces.length; i++) {{
                enlaces[i].addEventListener('click', function(e) {{
                    e.preventDefault();
                }});
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the page: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def guardar_html(html_content, ruta_salida):
    """
    Save HTML content to a file
    """
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            archivo.write(html_content)
        print(f"HTML file successfully saved at: {ruta_salida}")
        return True
    except Exception as e:
        print(f"Error saving HTML file: {e}")
        return False

def main():
    """
    Main function
    """
    print("Extracting AEMET content for Mérida...")
    html_content = extraer_contenido_aemet()
    
    if html_content:
        output_file = os.path.join(output_dir, "aemet.html")
        
        if guardar_html(html_content, output_file):
            print("Process completed successfully.")
        else:
            print("Could not save the HTML file.")
    else:
        print("Could not extract content from the page.")

if __name__ == "__main__":
    main()
