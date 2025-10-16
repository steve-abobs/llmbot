import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.config import get_settings
from llm.ollama import call_ollama
from mcp.weather import get_weather
from mcp.calendar import get_upcoming_events
from mcp.sheets import get_homework_for_today
from memory.json_memory import append_bot_message, append_user_message, get_context as mem_context
from kb.faiss_kb import query as kb_query

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("student-agent")

SYSTEM_PROMPT = (
    "You are a helpful school assistant. You can use tools to get information. "
    "If the user's question requires one of the tools, respond with a JSON object describing which tool to call. "
    "If not, respond directly to the user in natural language."
)


def _available_functions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "get_weather",
            "description": "Get current weather for a city via OpenWeatherMap",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": []},
        },
        {
            "name": "get_upcoming_events",
            "description": "Read upcoming events from Google Calendar",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "get_homework_for_today",
            "description": "Read today's homework from Google Sheets",
            "parameters": {"type": "object", "properties": {}},
        },
    ]


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/help — list commands\n"
        "/health — health check\n"
        "/weather [city] — current weather\n"
        "/schedule — upcoming events\n"
        "/homework — today's homework\n"
        "/ask <question> — tool-aware Q&A"
    )
    await update.message.reply_text(text)


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running")


async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else "Moscow"
    await update.message.reply_text(get_weather(city))


async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_upcoming_events())


async def homework_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_homework_for_today())


def _run_function_call(name: Optional[str], arguments: Dict[str, Any]) -> Optional[str]:
    if not name:
        return None
    try:
        if name == "get_weather":
            return get_weather(arguments.get("city", "Moscow"))
        if name == "get_upcoming_events":
            return get_upcoming_events()
        if name == "get_homework_for_today":
            return get_homework_for_today()
    except Exception as e:
        return f"Tool error: {e}"
    return None


async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = get_settings()
    user = update.effective_user
    if not user or not update.message:
        return
    user_id = str(user.id)
    query_text = update.message.text.split(" ", 1)
    question = query_text[1].strip() if len(query_text) > 1 else ""
    if not question:
        await update.message.reply_text("Usage: /ask <question>")
        return

    # Memory and KB context
    mem = mem_context(settings.memory_path, user_id=user_id, limit=10)
    kb_results = kb_query(settings.faiss_index_path, settings.faiss_meta_path, question, top_k=3)
    kb_texts = [f"KB: {r.get('title', '')}: {r.get('text', '')}" for r in kb_results]

    append_user_message(settings.memory_path, user_id, question)

    # First call: let model decide on tool usage
    functions = _available_functions()
    prompt = SYSTEM_PROMPT + "\n\nUser: " + question
    fc = call_ollama(prompt=prompt, functions=functions, context=mem + kb_texts)

    tool_result: Optional[str] = None
    if isinstance(fc, dict) and (fc.get("function") or fc.get("text")):
        if fc.get("function"):
            tool_result = _run_function_call(fc.get("function"), fc.get("arguments", {}))
        else:
            # Model answered directly
            final_answer = fc.get("text", "")
            append_bot_message(settings.memory_path, user_id, final_answer)
            await update.message.reply_text(final_answer)
            return

    # Second call: produce final user-facing answer with tool result in context
    context_lines = mem + kb_texts
    if tool_result:
        context_lines.append(f"TOOL_RESULT: {tool_result}")

    final = call_ollama(
        prompt=f"Answer the user's question clearly. Question: {question}",
        functions=None,
        context=context_lines,
    )
    final_text = final if isinstance(final, str) else final.get("text", "")
    if not final_text:
        final_text = tool_result or "I couldn't generate a response."

    append_bot_message(settings.memory_path, user_id, final_text)
    await update.message.reply_text(final_text)


def main():
    settings = get_settings()
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")
    application = Application.builder().token(settings.telegram_token).build()

    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("health", health_cmd))
    application.add_handler(CommandHandler("weather", weather_cmd))
    application.add_handler(CommandHandler("schedule", schedule_cmd))
    application.add_handler(CommandHandler("homework", homework_cmd))
    application.add_handler(CommandHandler("ask", ask_cmd))

    logger.info("Starting student-agent bot...")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
