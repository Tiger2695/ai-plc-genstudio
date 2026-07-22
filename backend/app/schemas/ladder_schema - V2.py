from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class PLCVariable(BaseModel):
    """Strictly maps the I/O Tag allocation according to IEC 61131-3 standards"""
    name: str = Field(..., description="Unique name of the Tag (e.g., I_Start_Button, O_Conveyor_Motor)")
    data_type: Literal["BOOL", "INT", "REAL", "TIME"] = Field(..., description="Standard PLC Data Type")
    address: Optional[str] = Field(None, description="Physical memory address mapping if required (e.g., %I0.0, %Q0.0)")
    description: str = Field(..., description="Functional description of what this variable controls")

class LadderComponent(BaseModel):
    """Defines an atomic instruction element within an industrial rung"""
    type: Literal["NO_CONTACT", "NC_CONTACT", "COIL", "LATCH_COIL", "UNLATCH_COIL", "TON_TIMER", "TOF_TIMER"] = Field(
        ..., description="The exact industrial electrical component type"
    )
    variable_name: str = Field(..., description="The associated tag name bounded to this instruction")
    preset_time: Optional[str] = Field(None, description="Required only for timers (e.g., T#5s, T#100ms)")

class LadderRung(BaseModel):
    """Represents a discrete functional rung evaluated from Left Rail to Right Rail"""
    rung_number: int = Field(..., description="Sequential index tracking execution flow")
    description: str = Field(..., description="Clear operator comment describing the safety/operational goal of this rung")
    
    # Series represents the sequential logical path (AND condition)
    # Inside each rung point, multiple items can run in parallel (OR condition)
    series_elements: List[LadderComponent] = Field(
        ..., description="Sequential execution chain on the rung. Every item in this list must evaluate to TRUE to pass execution."
    )

class PLCProgramPayload(BaseModel):
    """The complete verified engineering block compiled by the AI engine"""
    project_name: str = Field(..., description="Industrial project name code")
    variables_table: List[PLCVariable] = Field(..., description="The explicit Global/Local Tag allocation table")
    rungs: List[LadderRung] = Field(..., description="The ordered array of deterministic ladder logic circuits")
    
    # 💻 NEW FIELD: Structured Text / C++ Executable automation code block
    structured_text_code: str = Field(
        ..., 
        description="Complete industrial compliant Structured Text (ST / IEC 61131-3) automation source code representing the compiled ladder logic."
    )
    
    developer_notes: str = Field(..., description="Crucial deployment notes or safety edge cases highlighted by the assistant")