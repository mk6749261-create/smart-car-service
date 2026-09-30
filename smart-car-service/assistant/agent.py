"""
Agent orchestration (FR-30..FR-32, FR-39, FR-40) - Gemini function calling.

Design notes (documented per NFR-13):
- The server is stateless between HTTP requests: the client sends back the
  `conversation` list it received on the previous turn, and we send it back
  again extended with whatever happened. Each item is a plain dict shaped
  like the Gemini `contents` format: {"role": "user"|"model", "parts": [...]}.
- FR-40 (confirmation for critical actions): tools listed in
  CONFIRMATION_REQUIRED_TOOLS are never auto-executed. When the model
  requests one, we stop the loop immediately, return the conversation as-is
  (ending on that pending function_call part) plus a `pending_action`
  description, and wait for the caller to resend the same conversation with
  `confirm=True`. Only then do we actually run the tool.
- FR-39 (multi-step workflows): non-critical tools (read-only lookups) are
  executed immediately and the loop continues automatically, so the model
  can chain e.g. get_user_vehicles -> get_maintenance_history ->
  get_available_slots in a single user turn.
- We disable the SDK's automatic function calling (automatic_function_calling
  disabled) because we need to intercept book_appointment ourselves before
  it ever runs.
"""

import logging
import traceback

from django.conf import settings
from google import genai
from google.genai import types

from .tool_specs import TOOL_SPECS
from .tools import TOOLS, ToolError

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-flash-latest"
MAX_TOOL_ROUNDS = 6

# FR-40: these tools create/modify data and must never run without the
# user explicitly saying yes first.
CONFIRMATION_REQUIRED_TOOLS = {"book_appointment"}

SYSTEM_PROMPT = (
    "You are the AI Assistant for a Smart Car Service platform. You help the "
    "authenticated user with questions about their vehicles, maintenance "
    "history, available service appointments, and booking appointments.\n\n"
    "Rules you must always follow:\n"
    "- Only use the information returned by your tools. Never invent vehicle, "
    "maintenance, service or appointment details.\n"
    "- Before calling book_appointment, clearly summarise the vehicle, "
    "service and time slot to the user in plain language and make sure the "
    "conversation shows the user has agreed to it.\n"
    "- If a tool returns an error (for example, the user doesn't own a "
    "vehicle, or a slot is no longer available), explain that plainly to "
    "the user and suggest what they could do instead. Never expose raw "
    "error text or technical details.\n"
    "- If the user's request is unsupported, incomplete, or you don't have "
    "a tool for it, say so clearly instead of guessing."
)


def _client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _gemini_tool():
    declarations = [
        types.FunctionDeclaration(
            name=spec["name"],
            description=spec["description"],
            parameters=spec["input_schema"],
        )
        for spec in TOOL_SPECS
    ]
    return types.Tool(function_declarations=declarations)


def _config():
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[_gemini_tool()],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )


def _execute_tool(user, name, tool_input):
    """FR-33/FR-41: identity is already guaranteed by the view's
    IsAuthenticated check; each tool re-checks role/ownership itself."""
    handler = TOOLS.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return {"result": handler(user, tool_input or {})}
    except ToolError as exc:
        return {"error": str(exc)}
    except Exception:
        # NFR-09: never leak internals to the end user.
        return {"error": "Something went wrong while performing this action."}


def _parts_from_response(response):
    """Convert the model's response into our plain-dict part format."""
    parts = []
    candidate = response.candidates[0]
    for part in candidate.content.parts:
        if getattr(part, "function_call", None) is not None:
            parts.append(
                {
                    "function_call": {
                        "name": part.function_call.name,
                        "args": dict(part.function_call.args or {}),
                    }
                }
            )
        elif getattr(part, "text", None):
            parts.append({"text": part.text})
    return parts


def _text_from_parts(parts):
    return "".join(p.get("text", "") for p in parts if "text" in p)


def _function_calls_from_parts(parts):
    return [p["function_call"] for p in parts if "function_call" in p]


def run_agent(user, message, conversation=None, confirm=False):
    contents = list(conversation or [])
    client = _client()
    config = _config()

    if confirm:
        # التعامل مع تأكيد الحجز المسبق
        last = contents[-1] if contents else None
        pending_calls = (
            _function_calls_from_parts(last.get("parts", []))
            if last and last.get("role") == "model"
            else []
        )
        if not pending_calls:
            return {
                "reply": "There's nothing pending for me to confirm right now.",
                "requires_confirmation": False,
                "pending_action": None,
                "conversation": contents,
            }
        response_parts = []
        for call in pending_calls:
            outcome = _execute_tool(user, call["name"], call.get("args"))
            response_parts.append(
                {"function_response": {"name": call["name"], "response": outcome}}
            )
        contents.append({"role": "user", "parts": response_parts})
    else:
        contents.append({"role": "user", "parts": [{"text": message}]})

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            # 🎯 تحويل الـ dicts إلى كائنات Pydantic الرسمية المتوافقة مع الـ SDK الجديد
            pydantic_contents = []
            for item in contents:
                converted_parts = []
                for p in item.get("parts", []):
                    if "text" in p:
                        converted_parts.append(types.Part.from_text(text=p["text"]))
                    elif "function_call" in p:
                        converted_parts.append(
                            types.Part(
                                function_call=types.FunctionCall(
                                    name=p["function_call"]["name"],
                                    args=p["function_call"]["args"]
                                )
                            )
                        )
                    elif "function_response" in p:
                        converted_parts.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=p["function_response"]["name"],
                                    response=p["function_response"]["response"]
                                )
                            )
                        )
                
                pydantic_contents.append(
                    types.Content(role=item.get("role"), parts=converted_parts)
                )

            # استدعاء السيرفر بالكائنات المعدلة والمحمية بـ Pydantic
            response = client.models.generate_content(
                model=MODEL_NAME, contents=pydantic_contents, config=config
            )
        except Exception:
            print("=" * 60)
            print("GEMINI API CALL FAILED:")
            traceback.print_exc()
            print("=" * 60)
            logger.exception("Gemini API call failed in run_agent")
            return {
                "reply": "I'm having trouble reaching the assistant service right now. Please try again in a moment.",
                "requires_confirmation": False,
                "pending_action": None,
                "conversation": contents,
            }
            
        model_parts = _parts_from_response(response)
        contents.append({"role": "model", "parts": model_parts})

        calls = _function_calls_from_parts(model_parts)
        if not calls:
            return {
                "reply": _text_from_parts(model_parts),
                "requires_confirmation": False,
                "pending_action": None,
                "conversation": contents,
            }

        needs_confirmation = [c for c in calls if c["name"] in CONFIRMATION_REQUIRED_TOOLS]
        if needs_confirmation:
            call = needs_confirmation[0]  # تم إصلاح قراءة العنصر الأول هنا
            return {
                "reply": _text_from_parts(model_parts) or "I need your confirmation before I do that.",
                "requires_confirmation": True,
                "pending_action": {"name": call["name"], "input": call["args"]},
                "conversation": contents,
            }

        response_parts = []
        for call in calls:
            outcome = _execute_tool(user, call["name"], call.get("args"))
            response_parts.append(
                {"function_response": {"name": call["name"], "response": outcome}}
            )
        contents.append({"role": "user", "parts": response_parts})

    return {
        "reply": "I couldn't finish that request in a reasonable number of steps. Could you rephrase it?",
        "requires_confirmation": False,
        "pending_action": None,
        "conversation": contents,
    }
