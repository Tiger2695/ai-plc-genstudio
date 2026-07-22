# delta_rules.py
from pydantic import BaseModel, Field, field_validator
import re

class DeltaTag(BaseModel):
    name: str = Field(..., description="System naming variable identifier")
    data_type: str = Field(..., description="Data type specification (e.g. BOOL, INT, WORD)")
    address: str = Field(..., description="Delta physical or memory address register")
    description: str = Field(..., description="Functional context mapping")

    @field_validator('address')
    @classmethod
    def validate_delta_address(cls, v: str) -> str:
        v = v.upper().strip()
        
        # 1. Digital Input Boundary Check (X0.0 - X63.15)
        if v.startswith('X'):
            match = re.match(r'^X(\d+)\.(\d+)$', v)
            if not match:
                raise ValueError(f"Delta Input Tag Syntax Error: {v}. Must match X0.0 format.")
            word, bit = map(int, match.groups())
            if not (0 <= word <= 63 and 0 <= bit <= 15):
                raise ValueError(f"Delta Hardware Input Out of Range (X0.0 to X63.15): {v}")
        
        # 2. Digital Output Boundary Check (Y0.0 - Y63.15)
        elif v.startswith('Y'):
            match = re.match(r'^Y(\d+)\.(\d+)$', v)
            if not match:
                raise ValueError(f"Delta Output Tag Syntax Error: {v}. Must match Y0.0 format.")
            word, bit = map(int, match.groups())
            if not (0 <= word <= 63 and 0 <= bit <= 15):
                raise ValueError(f"Delta Hardware Output Out of Range (Y0.0 to Y63.15): {v}")
        
        # 3. Data Register Word Check (D0 - D29999)
        elif v.startswith('D'):
            match = re.match(r'^D(\d+)$', v)
            if not match:
                raise ValueError(f"Delta Data Register Syntax Error: {v}. Must match D0 format.")
            reg_num = int(match.group(1))
            if not (0 <= reg_num <= 29999):
                raise ValueError(f"Delta Data Register Word Out of Range (D0 to D29999): {v}")
        
        # 4. Internal Memory Bit Check (M0 - M8191)
        elif v.startswith('M'):
            match = re.match(r'^M(\d+)$', v)
            if not match:
                raise ValueError(f"Delta Memory Bit Syntax Error: {v}. Must match M0 format.")
            bit_num = int(match.group(1))
            if not (0 <= bit_num <= 8191):
                raise ValueError(f"Delta Internal Software Flag Out of Range (M0 to M8191): {v}")
                
        # 5. 🆕 Timer Register Check (T0 - T511)
        elif v.startswith('T'):
            match = re.match(r'^T(\d+)$', v)
            if not match:
                raise ValueError(f"Delta Timer Register Syntax Error: {v}. Must match T0 format.")
            timer_num = int(match.group(1))
            if not (0 <= timer_num <= 511):
                raise ValueError(f"Delta Timer Out of Range (T0 to T511): {v}")

        # 6. 🆕 Counter Register Check (C0 - C511)
        elif v.startswith('C'):
            match = re.match(r'^C(\d+)$', v)
            if not match:
                raise ValueError(f"Delta Counter Register Syntax Error: {v}. Must match C0 format.")
            counter_num = int(match.group(1))
            if not (0 <= counter_num <= 511):
                raise ValueError(f"Delta Counter Out of Range (C0 to C511): {v}")
                
        else:
            raise ValueError(f"Unknown Device Type Token: {v}. Must map to Delta Registers (X, Y, M, D, T, C).")
            
        return v