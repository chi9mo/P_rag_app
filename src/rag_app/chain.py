from collections.abc import Generator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_qdrant import QdrantVectorStore

LLM_MODEL = "qwen3:14b"

# RAG精度評価のための、シンプルなプロンプト。
SYSTEM_PROMPT_TEMPLATE = """\
あなたは資料に基づいて質問に答えるアシスタントです。
以下のコンテキストのみを根拠に、日本語で回答してください。
コンテキストに情報がない場合は「資料に記載がありません」とだけ答えてください。

コンテキスト:
{context}"""

# # 実際に使う時用のプロンプト⇩
# SYSTEM_PROMPT_TEMPLATE = """\
# あなたは医薬品の専門アシスタントです。
# 以下のコンテキストを根拠に、患者や医療従事者が理解しやすいよう\
# 自分の言葉でわかりやすく日本語で説明してください。
# 箇条書きや見出しを使って整理し、難しい用語は噛み砕いて補足してください。
# コンテキストに情報がない場合は「資料に記載がありません」と答えてください。

# コンテキスト:
# {context}"""

llm = ChatOllama(model=LLM_MODEL, streaming=True)


def ask(
    question: str,
    history: list[tuple[str, str]],
    vectorstore: QdrantVectorStore,
) -> tuple[Generator[str, None, None], list]:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    source_docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in source_docs)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)

    messages = [SystemMessage(content=system_prompt)]
    for human_msg, ai_msg in history:
        messages.append(HumanMessage(content=human_msg))
        messages.append(AIMessage(content=ai_msg))
    messages.append(HumanMessage(content=question))

    def stream() -> Generator[str, None, None]:
        for chunk in llm.stream(messages):
            yield chunk.content

    return stream(), source_docs
