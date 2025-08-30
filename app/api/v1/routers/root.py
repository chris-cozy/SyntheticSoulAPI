from fastapi import APIRouter, HTTPException
from app.constants.schemas import get_thought_schema
from app.services.openai import get_structured_response

router = APIRouter(tags=["root"]) # no prefix; mounted at "/"

@router.get("/")
async def root():
    try:
        response = await get_structured_response(
        [{"role": "user", "content": "Please give me a random thought."}],
        get_thought_schema(),
        )
        return {"message": response["thought"]}
    except Exception as e:
        print(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))