from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional
import re


class PLCVariable(BaseModel):
    name: str = Field(
        ...,
        description="Unique tag name. If unavailable, use the address."
    )
    data_type: Literal["BOOL", "INT", "REAL", "TIME", "WORD"] = Field(
        ...,
        description="Standard PLC data type."
    )
    address: str = Field(
        ...,
        description="PLC address (X, Y, M, T, C, D etc.)."
    )
    description: Optional[str] = Field(
        None,
        description="Functional description."
    )


class LadderComponent(BaseModel):
    type: Literal[
        "NO_CONTACT",
        "NC_CONTACT",
        "COIL",
        "LATCH_COIL",
        "UNLATCH_COIL",
        "TON",
        "TOF",
        "CTU",
        "TMR",
    ] = Field(
        ...,
        description="PLC ladder element type (supports Delta style TMR blocks)."
    )

    variable_name: str = Field(
        ...,
        description="Must match a PLCVariable.name (e.g. timer address like T0)."
    )

    preset_time: Optional[str] = Field(
        None,
        description="Required for timers. Can be IEC format (T#10s) or Delta integer/raw preset (e.g., 100, K100)."
    )

    @field_validator("preset_time", mode="before")
    @classmethod
    def clean_preset_time(cls, v: Optional[str]) -> Optional[str]:
        """
        Accepts raw integer strings or Delta style presets and normalizes them safely.
        """
        if v is None:
            return None
        return str(v).strip()


class LadderRung(BaseModel):
    rung_number: int

    description: Optional[str] = Field(
        None,
        description="Optional network description."
    )

    series_elements: List[LadderComponent] = Field(
        ...,
        description=(
            "Ordered ladder elements. "
            "Contacts, instruction blocks (TON/TOF/CTU/TMR), etc. "
            "Timers MUST appear here as instruction blocks."
        )
    )

    parallel_branches: Optional[List[List[LadderComponent]]] = Field(
        default=None,
        description="Optional parallel branches."
    )

    output_coil: Optional[LadderComponent] = Field(
        default=None,
        description=(
            "Optional final output coil. "
            "Use ONLY for COIL, LATCH_COIL or UNLATCH_COIL. "
            "Leave null when the rung terminates with an instruction block "
            "such as TON, TOF, CTU, or TMR."
        )
    )


class PLCProgramPayload(BaseModel):
    project_name: str = Field(
        ...,
        description="Project name."
    )

    variables_table: List[PLCVariable]

    rungs: List[LadderRung]

    structured_text_code: Optional[str] = Field(
        None,
        description="Optional Structured Text."
    )

    developer_notes: Optional[str] = Field(
        None,
        description="Optional developer notes."
    )