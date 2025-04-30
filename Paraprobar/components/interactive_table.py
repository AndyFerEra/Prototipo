import reflex as rx

def interactive_table(data: list[dict]) -> rx.Component:

    return rx.raw(
        """
        <div id="hot"></div>
        <script>
            document.addEventListener("DOMContentLoaded", function () {
                const container = document.getElementById("hot");
                const hot = new Handsontable(container, {
                    data: %s,
                    colHeaders: true,
                    rowHeaders: true,
                    licenseKey: "non-commercial-and-evaluation",
                    stretchH: "all",
                    manualColumnResize: true,
                    manualRowResize: true,
                    filters: true,
                    dropdownMenu: true,
                });
            });
        </script>
        """ % data
    )