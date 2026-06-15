import gradio as gr

from bookscope import ENRICHED_COLUMNS, SCAN_COLUMNS, enrich_books, scan_shelf_image


APP_CSS = """
.bookscope-shell {max-width: 1180px; margin: 0 auto;}
.bookscope-title h1 {font-size: 30px; line-height: 1.1; margin-bottom: 2px;}
.bookscope-title p {margin-top: 0; color: #59636e;}
"""


def scan_action(image):
    table, status = scan_shelf_image(image)
    return table, status


def enrich_action(table):
    enriched, status = enrich_books(table)
    return enriched, status


with gr.Blocks(title="Bookscope") as demo:
    with gr.Column(elem_classes=["bookscope-shell"]):
        gr.Markdown(
            """
            <div class="bookscope-title">
              <h1>Bookscope</h1>
              <p>Messy shelf photo in. Searchable used-book inventory out.</p>
            </div>
            """
        )

        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=320):
                shelf_image = gr.Image(
                    label="Shelf photo",
                    sources=["upload", "webcam"],
                    type="pil",
                    height=380,
                )
                with gr.Row():
                    scan_button = gr.Button("Scan shelf", variant="primary")
                    enrich_button = gr.Button("Enrich rows")
                status = gr.Textbox(label="Status", interactive=False, lines=3)

            with gr.Column(scale=7, min_width=420):
                scan_results = gr.Dataframe(
                    headers=SCAN_COLUMNS,
                    label="Detected books",
                    interactive=True,
                    row_count=(4, "dynamic"),
                    column_count=(len(SCAN_COLUMNS), "fixed"),
                    wrap=True,
                )
                enriched_results = gr.Dataframe(
                    headers=ENRICHED_COLUMNS,
                    label="Enriched inventory",
                    interactive=True,
                    row_count=(4, "dynamic"),
                    column_count=(len(ENRICHED_COLUMNS), "fixed"),
                    wrap=True,
                )

        scan_button.click(
            scan_action,
            inputs=shelf_image,
            outputs=[scan_results, status],
        )
        enrich_button.click(
            enrich_action,
            inputs=scan_results,
            outputs=[enriched_results, status],
        )


if __name__ == "__main__":
    demo.launch(css=APP_CSS, theme=gr.themes.Soft())
