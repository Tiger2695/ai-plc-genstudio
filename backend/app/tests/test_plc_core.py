import pytest
from pydantic import BaseModel, Field, field_validator
import re

# =============================================================================
# 1. HARDWARE BOUNDS SCHEMA (Strict V2 Validation)
# =============================================================================
class DeltaAddressValidator(BaseModel):
    variable_name: str
    address: str

    @field_validator("address")
    @classmethod
    def validate_delta_bounds(cls, addr: str) -> str:
        addr = addr.upper().strip()
        # Inputs: X0.0 to X63.15
        if addr.startswith("X"):
            match = re.match(r"^X(\d+)\.(\d+)$", addr)
            if not match or not (0 <= int(match.group(1)) <= 63) or not (0 <= int(match.group(2)) <= 15):
                raise ValueError(f"Out of bounds Delta Input: {addr}")
        # Outputs: Y0.0 to Y63.15
        elif addr.startswith("Y"):
            match = re.match(r"^Y(\d+)\.(\d+)$", addr)
            if not match or not (0 <= int(match.group(1)) <= 63) or not (0 <= int(match.group(2)) <= 15):
                raise ValueError(f"Out of bounds Delta Output: {addr}")
        return addr

# =============================================================================
# 2. EMULATED PLC SCAN ENGINE (Desi Logic Simulator)
# =============================================================================
class DeltaPLCEmulator:
    def __init__(self):
        # Physical Inputs
        self.X0_0 = False  # Start Button
        self.X0_1 = False  # Stop Button (Normally Open physical contact assumed here)
        # Physical Outputs
        self.Y0_0 = False  # Motor Run

    def set_inputs(self, start: bool, stop: bool):
        self.X0_0 = start
        self.X0_1 = stop

    def execute_scan_cycle(self):
        """
        Equivalent to Delta Structured Text:
        Y0.0 := (X0.0 OR Y0.0) AND NOT X0.1;
        """
        # Network 1 & 2 combined evaluation
        self.Y0_0 = (self.X0_0 or self.Y0_0) and not self.X0_1


# =============================================================================
# 3. PRODUCTION TEST CASES
# =============================================================================
def test_delta_address_boundaries():
    """Verify that generated hardware tags conform to Delta AS228 specification."""
    # Valid Cases
    assert DeltaAddressValidator(variable_name="Start", address="X0.0")
    assert DeltaAddressValidator(variable_name="Pump", address="Y1.12")
    
    # Invalid Cases (Should Raise Exception)
    with pytest.raises(ValueError):
        DeltaAddressValidator(variable_name="Faulty_Input", address="X64.0") # Max input is X63
    with pytest.raises(ValueError):
        DeltaAddressValidator(variable_name="Faulty_Output", address="Y2.16") # Bit offset max is 15


def test_motor_latching_sequence():
    """Verify state transitions of the latching circuit over consecutive scan cycles."""
    plc = DeltaPLCEmulator()
    
    # Init: Machine is Idle
    plc.execute_scan_cycle()
    assert plc.Y0_0 is False, "Initial state must be OFF"

    # Step 1: Push START Button (X0.0 = True)
    plc.set_inputs(start=True, stop=False)
    plc.execute_scan_cycle()
    assert plc.Y0_0 is True, "Motor should start when Start Button is pressed"

    # Step 2: Release START Button (X0.0 = False) -> Logic should LATCH
    plc.set_inputs(start=False, stop=False)
    plc.execute_scan_cycle()
    assert plc.Y0_0 is True, "Motor must stay latched after releasing Start Button"

    # Step 3: Trigger STOP Button (X0.1 = True) -> Logic must UNLATCH
    plc.set_inputs(start=False, stop=True)
    plc.execute_scan_cycle()
    assert plc.Y0_0 is False, "Motor must stop instantly when Stop Button is pressed"


def test_safety_stop_override():
    """Ensure STOP button has absolute priority even if START is held down."""
    plc = DeltaPLCEmulator()
    
    # Both Start and Stop are pressed simultaneously
    plc.set_inputs(start=True, stop=True)
    plc.execute_scan_cycle()
    assert plc.Y0_0 is False, "Safety critical failure: Stop button did not override Start!"