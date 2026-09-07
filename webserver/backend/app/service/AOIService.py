import uuid
from app.Security import decode_jwt
from app.repo.AOIRequestRepo import AOIRequestRepo
from app.model.execution.request.AOIRequest import AOIRequest
from app.service.DemoService import get_demo_areas

def get_user_AOI_list(user_jwt: str):
    #stub function to return user-specific AOI requests, in a real scenario this would fetch data from a database 
    return get_demo_areas()  # For demonstration, returning demo areas for any user
    email = decode_jwt(user_jwt)["sub"]
    return AOIRequestRepo.list_for_email(email)

def create_user_AOI(user_jwt: str, payload: AOIRequest):
    email = decode_jwt(user_jwt)["sub"]
    request_id = str(uuid.uuid4())
    return AOIRequestRepo.save(request_id, email, payload)