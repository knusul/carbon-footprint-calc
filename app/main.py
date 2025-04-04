from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
import os
from dotenv import load_dotenv
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload
from app.models.carbon_footprint_response import CarbonFootprintResponse
from app.models.token import Token
from app.services.calculate_carbon_footprint import CalculateCarbonFootprint
from app.services.verify_jwt_token import verify_jwt_token
from app.services.get_scopes_data import get_scopes_data
from app.services.get_energy_sources import get_energy_sources
import jwt

load_dotenv()

app = FastAPI()

# OAuth2 password bearer scheme to receive JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_jwt_token(token)

# lookup controller for swagger to create JWT token from username/password
# after successful auth swagger ui adds JWT token to request headers 
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = os.getenv("USERNAME", "testuser")
    password = os.getenv("PASSWORD", "testpassword")
    
    if form_data.username == username and form_data.password == password:
        SECRET_KEY = os.getenv("SECRET_KEY")
        ALGORITHM = os.getenv("ALGORITHM")
        token = jwt.encode({"sub": form_data.username}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )

@app.post("/carbon-footprint", response_model=List[CarbonFootprintResponse])
async def calculate_co2_balance(
    energy_entries: List[CarbonFootprintRequestPayload], 
    current_user: dict = Depends(get_current_user)  # Force token verification
):
    # This logic does not belong to a controller responsibility. Think about refactoring it and moving away from the controller.
    try:
        energy_sources = get_energy_sources()
        scopes_data = get_scopes_data()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
    service = CalculateCarbonFootprint(energy_sources, scopes_data)
    result = service.calculate_co2_balance(energy_entries)
    return result
