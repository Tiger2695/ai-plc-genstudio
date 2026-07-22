import json
from google import genai
from google.genai import types
from ..core.config import settings
from ..schemas.ladder_schema import PLCProgramPayload
import logging



class PLCLLMService:
    def __init__(self):
        """Initialize the modern Gemini Client using system settings"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("🚨 GEMINI_API_KEY missing! System cannot initialize AI Orchestration Layer.")
        
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = getattr(settings, "GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")

    def _build_system_instruction(self) -> str:
        return """
    You are an Industrial PLC Ladder Logic JSON Translator.

    Your ONLY responsibility is translating the user's request into the required PLC JSON schema.

    You are NOT a PLC designer.
    You are NOT allowed to optimize logic.
    You are NOT allowed to invent hardware.
    You are NOT allowed to add safety devices.
    You are NOT allowed to create additional variables.

    --------------------------------------------------
    GENERAL RULES
    --------------------------------------------------

    1. Return ONLY valid JSON matching the supplied schema.

    2. Never create additional fields.

    3. Never omit required fields.

    4. Never rename schema fields.

    5. Never explain your reasoning.

    6. Never generate markdown.

    --------------------------------------------------
    VARIABLE RULES
    --------------------------------------------------

    Only create variables explicitly required by the user's prompt.

    Examples

    User:
    Control Y0.0 using X0.0

    Variables:

    X0.0
    Y0.0

    NOT allowed:

    M0
    M100
    Sensor1
    Emergency_Stop
    Enable_Bit

    --------------------------------------------------
    RUNG RULES
    --------------------------------------------------

    series_elements contains:

    • Contacts
    • Function Blocks
    • Timers
    • Counters

    output_coil contains ONLY:

    COIL

    LATCH_COIL

    UNLATCH_COIL

    If a rung ends with an instruction block,
    output_coil MUST be null.

    --------------------------------------------------
    TIMER RULES
    --------------------------------------------------

    Timers are Function Blocks.

    They NEVER appear as output coils.

    Correct:

    series_elements

    [
    {
    "type":"NO_CONTACT",
    "variable_name":"X0.1"
    },
    {
    "type":"TON",
    "variable_name":"T0",
    "preset_time":"T#10s"
    }
    ]

    output_coil = null

    Incorrect:

    output_coil =
    {
    "type":"TON"
    }

    --------------------------------------------------
    CONTACT RULES
    --------------------------------------------------

    A timer done bit (T0)

    IS allowed

    ONLY when the user logic requires it.

    Example

    Rung 1

    X0.1

    TON T0

    Rung 2

    T0

    Y0.1

    --------------------------------------------------
    OUTPUT RULES
    --------------------------------------------------

    Generate deterministic industrial ladder logic.

    No creativity.

    No optimization.

    No assumptions.

    No additional networks.
    """

    async def generate_ladder_logic(self, user_prompt: str) -> PLCProgramPayload:
        """
        Sends the prompt to Gemini with zero-hallucination constraints 
        and deterministic temperature.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt, # Optimized to ONLY pass the user prompt
                config=types.GenerateContentConfig(
                    system_instruction=self._build_system_instruction(),
                    temperature=0.0, # Set for absolute determinism
                    response_mime_type="application/json",
                    response_schema=PLCProgramPayload,
                ),
            )
            
            parsed_json = json.loads(response.text)
            logging.info(response.text)
            return PLCProgramPayload(**parsed_json)

        except Exception as e:
            raise RuntimeError(f"🚨 LLM MAPPING EXECUTION FAILED: {str(e)}")