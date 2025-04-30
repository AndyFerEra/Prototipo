import reflex as rx
from typing import List, Dict, Any

def handsontable_editor(
    data: List[Dict[str, Any]], 
    columns: List[str],
    height: str = "500px",
) -> rx.Component:
    
    # formato JavaScript
    js_data = rx.utils.format.format_value(data)
    js_columns = rx.utils.format.format_value(columns)
    
    return rx.box(
        # Contenedor Handsontable
        rx.html(
            f"""
            <div id="hot-app" style="width: 100%; height: {height};"></div>
            """
        ),
        
        # scripts necesarios
        rx.script(src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"),
        rx.style(href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css"),
        
        # Ini Handsontable
        rx.script(
            f"""
            document.addEventListener('DOMContentLoaded', function() {{
                const container = document.getElementById('hot-app');
                const hot = new Handsontable(container, {{
                    data: {js_data},
                    colHeaders: {js_columns},
                    rowHeaders: true,
                    height: '{height}',
                    width: '100%',
                    licenseKey: 'non-commercial-and-evaluation',
                    stretchH: 'all',
                    autoColumnSize: true,
                    manualRowResize: true,
                    manualColumnResize: true,
                    contextMenu: true,
                    filters: true,
                    dropdownMenu: true,
                    columnSorting: true,
                    minSpareRows: 1,
                    afterChange: function(changes) {{
                        if (changes) {{
                            console.log('Datos actualizados:', this.getData());
                        }}
                    }}
                }});
                
                window.hotInstance = hot;
            }});
            """
        ),
        width="100%",
    )