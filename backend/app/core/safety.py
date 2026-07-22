import re
from typing import Dict, List, Tuple
from ..schemas.ladder_schema import PLCProgramPayload, LadderRung

class PLCSafetyEngine:
    """
    Deterministic Industrial Safety Rules Engine.
    Cross-verifies AI output against hardcoded Delta AS228 hardware bounds and guidelines.
    """

    @staticmethod
    def verify_delta_hardware_bounds(payload: PLCProgramPayload) -> Tuple[bool, List[str]]:
        """
        Rule 0: Delta AS228 Hardware Address Range Verification.
        Ensures AI hasn't hallucinated registers beyond physical CPU bounds.
        """
        errors: List[str] = []
        
        # Regex patterns for strict Delta AS228 validation
        input_pattern = re.compile(r'^X([0-9]|[1-5][0-9]|6[0-3])\.([0-9]|1[0-5])$') # X0.0 to X63.15
        output_pattern = re.compile(r'^Y([0-9]|[1-5][0-9]|6[0-3])\.([0-9]|1[0-5])$') # Y0.0 to Y63.15
        m_bit_pattern = re.compile(r'^M([0-9]|[1-9][0-9]{1,2}|[1-7][0-9]{3}|8[0-1][0-9][0-1])$') # M0 to M8191
        d_reg_pattern = re.compile(r'^D([0-9]|[1-9][0-9]{1,3}|[1-2][0-9]{4}|30000)$') # D0 to D30000
        timer_pattern = re.compile(r'^T([0-9]|[1-4][0-9]{2}|5[0-1][0-1])$') # T0 to T511
        counter_pattern = re.compile(r'^C([0-9]|[1-4][0-9]{2}|5[0-1][0-1])$') # C0 to C511

        for var in payload.variables_table:
            addr = var.address.strip().upper()
            
            # Check Inputs
            if addr.startswith('X'):
                if not input_pattern.match(addr):
                    errors.append(f"🚨 HARDWARE BOUND FAULT: Input address '{addr}' is out of Delta AS228 range (X0.0 - X63.15).")
            # Check Outputs
            elif addr.startswith('Y'):
                if not output_pattern.match(addr):
                    errors.append(f"🚨 HARDWARE BOUND FAULT: Output address '{addr}' is out of Delta AS228 range (Y0.0 - Y63.15).")
            # Check Memory Bits
            elif addr.startswith('M'):
                if not m_bit_pattern.match(addr):
                    errors.append(f"🚨 HARDWARE BOUND FAULT: Memory Bit '{addr}' is out of Delta AS228 range (M0 - M8191).")
            # Check Timers
            elif addr.startswith('T'):
                if not timer_pattern.match(addr):
                    errors.append(f"🚨 HARDWARE BOUND FAULT: Timer Register '{addr}' is out of Delta AS228 range (T0 - T511).")
            # Check Counters
            elif addr.startswith('C'):
                if not counter_pattern.match(addr):
                    errors.append(f"🚨 HARDWARE BOUND FAULT: Counter Register '{addr}' is out of Delta AS228 range (C0 - C511).")
            # Check Data/Analog Registers
            elif addr.startswith('D'):
                if not d_reg_pattern.match(addr):
                    errors.append(f"🚨 HARDWARE BOUND FAULT: Data Register '{addr}' is out of Delta AS228 range (D0 - D30000).")

        return len(errors) == 0, errors

    @staticmethod
    def verify_double_coils(payload: PLCProgramPayload) -> Tuple[bool, List[str]]:
        """
        Rule 1: Double Coil Fault Detection
        A unique physical output address or normal coil variable MUST NOT be written to in multiple rungs.
        """
        coil_registry: Dict[str, List[int]] = {}
        errors: List[str] = []

        for rung in payload.rungs:
            for element in rung.series_elements:
                if element.type == "COIL":
                    var_name = element.variable_name
                    if var_name not in coil_registry:
                        coil_registry[var_name] = []
                    coil_registry[var_name].append(rung.rung_number)

        for var_name, rungs in coil_registry.items():
            if len(rungs) > 1:
                errors.append(
                    f"🚨 DOUBLE COIL FAULT: Variable '{var_name}' is written as a normal COIL in multiple rungs: {rungs}. "
                    f"This creates deterministic race conditions in PLC cyclical scans. Use LATCH/UNLATCH instead."
                )

        return len(errors) == 0, errors

    @staticmethod
    def verify_emergency_interlocking(payload: PLCProgramPayload) -> Tuple[bool, List[str]]:
        """
        Rule 2: Emergency Stop Interlock Check
        """
        errors: List[str] = []
        e_stop_tags = [var.name for var in payload.variables_table if "E_Stop" in var.name or "Emergency" in var.name]
        
        if not e_stop_tags:
            return True, []

        for rung in payload.rungs:
            has_actuator_output = any(
                el.type in ["COIL", "LATCH_COIL"] and not el.variable_name.lower().endswith("timer") 
                for el in rung.series_elements
            )
            
            if has_actuator_output:
                interlocked = any(el.variable_name in e_stop_tags for el in rung.series_elements)
                if not interlocked:
                    errors.append(
                        f"⚠️ SAFETY INTERLOCK BREACH: Rung {rung.rung_number} controls an actuator but does NOT "
                        f"integrate an Emergency Stop switch interlock branch."
                    )

        return len(errors) == 0, errors

    @staticmethod
    def verify_timers_and_counters(payload: PLCProgramPayload) -> Tuple[bool, List[str]]:
        """
        Rule 3: Timer & Counter Parameters Validation
        """
        errors: List[str] = []

        for rung in payload.rungs:
            for element in rung.series_elements:
                if element.type in ["TON_TIMER", "TOF_TIMER", "CTU_COUNTER"]:
                    if not element.preset_time or not element.preset_time.strip():
                        errors.append(
                            f"🚨 PARAMETER FAULT: Rung {rung.rung_number} uses a '{element.type}' block for "
                            f"'{element.variable_name}', but the Preset Value/Time is empty!"
                        )
                    elif "TIMER" in element.type and not element.preset_time.startswith("T#"):
                        errors.append(
                            f"⚠️ SYNTAX WARNING: Rung {rung.rung_number} timer preset '{element.preset_time}' "
                            f"should follow IEC 61131-3 standards (e.g., T#5s, T#200ms)."
                        )

        return len(errors) == 0, errors

    @classmethod
    def execute_safety_audit(cls, payload: PLCProgramPayload) -> Dict[str, any]:
        """
        Runs all validation including the new hardware boundaries module.
        """
        hw_pass, hw_errors = cls.verify_delta_hardware_bounds(payload)
        double_coil_pass, double_coil_errors = cls.verify_double_coils(payload)
        safety_pass, safety_errors = cls.verify_emergency_interlocking(payload)
        timer_counter_pass, timer_counter_errors = cls.verify_timers_and_counters(payload)
        
        all_errors = hw_errors + double_coil_errors + safety_errors + timer_counter_errors
        audit_passed = hw_pass and double_coil_pass and safety_pass and timer_counter_pass

        return {
            "audit_passed": audit_passed,
            "error_count": len(all_errors),
            "safety_logs": all_errors if not audit_passed else ["✅ All industrial deterministic safety criteria passed successfully."]
        }