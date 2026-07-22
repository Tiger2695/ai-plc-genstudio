from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError # Import included
from app.services.llm_service import PLCLLMService
from app.core.safety import PLCSafetyEngine
from app.schemas.ladder_schema import PLCProgramPayload
from app.core.delta_rules import DeltaTag 

router = APIRouter()
llm_service = PLCLLMService()

# PromptRequest class included
class PromptRequest(BaseModel):
    prompt: str = Field(..., example="Control Y0.0 by X0.0")

@router.post("/generate", response_model=dict)
async def generate_plc_logic(request: PromptRequest):
    """
    Core industrial route: Deterministic compilation pipeline with 
    strict exception handling and validation.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt empty nahi ho sakta, Dada!")

    try:
        # Step 1: AI Compilation
        compiled_payload: PLCProgramPayload = await llm_service.generate_ladder_logic(request.prompt)
        
        # Step 1.5: Validate generated logic variables
        if not compiled_payload.variables_table:
             raise HTTPException(status_code=422, detail="No PLC variables generated from the prompt.")

        for var in compiled_payload.variables_table:
            try:
                # Safely cast and sanitize fields to prevent type mismatch violations
                DeltaTag(
                    name=str(var.name) if var.name is not None else "",
                    data_type=str(var.data_type) if var.data_type is not None else "BOOL",
                    address=str(var.address) if var.address is not None else "T0",
                    description=str(var.description) if var.description is not None else ""
                )
            except ValidationError as val_err:
                raise HTTPException(
                    status_code=422, 
                    detail=f"Delta AS228 Hardware Violation: {val_err.errors()[0]['msg']}"
                )

        # Step 2: Deterministic Safety Check
        safety_audit_results = PLCSafetyEngine.execute_safety_audit(compiled_payload)
        
        return {
            "status": "success",
            "data": compiled_payload.model_dump(exclude_none=True),
            "safety_audit": safety_audit_results
        }
        
    except HTTPException:
        # HTTP errors preserve karo
        raise
    except Exception as e:
        # Unexpected errors ko wrap karo
        raise HTTPException(
            status_code=500, 
            detail=f"Pipeline Execution Error: {str(e)}"
        )