import gradio as gr

from rag_app.chain import ask
from rag_app.indexer import build_index

vectorstore = build_index()


def _format_sources(docs: list) -> str:
    if not docs:
        return "出典なし"
    lines = []
    for doc in docs:
        page = doc.metadata.get("page", "?")
        content = doc.page_content[:200].replace("\n", " ")
        lines.append(f"**p.{page}** — {content}...")
    return "\n\n".join(lines)


def respond(message: str, chatbot: list):
    if not message.strip():
        yield chatbot, ""
        return

    history = [
        (chatbot[i]["content"], chatbot[i + 1]["content"])
        for i in range(0, len(chatbot) - 1, 2)
        if chatbot[i]["role"] == "user" and chatbot[i + 1]["role"] == "assistant"
    ]

    stream, source_docs = ask(message, history, vectorstore)

    chatbot = chatbot + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": ""},
    ]

    for token in stream:
        chatbot[-1]["content"] += token
        yield chatbot, gr.update()

    yield chatbot, _format_sources(source_docs)


def reset() -> tuple:
    return [], ""


with gr.Blocks(title="RAG チャット") as demo:
    gr.Markdown("# RAG チャット — guideline.pdf")

    chatbot = gr.Chatbot(height=500)

    with gr.Accordion("出典", open=False):
        sources_display = gr.Markdown()

    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="質問を入力してください...",
            scale=4,
            show_label=False,
            autofocus=True,
        )
        submit_btn = gr.Button("送信", scale=1, variant="primary")

    reset_btn = gr.Button("リセット")

    submit_args = dict(fn=respond, inputs=[msg_input, chatbot], outputs=[chatbot, sources_display])
    submit_btn.click(**submit_args).then(lambda: "", outputs=msg_input)
    msg_input.submit(**submit_args).then(lambda: "", outputs=msg_input)
    reset_btn.click(reset, outputs=[chatbot, sources_display])


if __name__ == "__main__":
    demo.launch()
