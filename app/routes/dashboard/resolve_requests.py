from flask_login import current_user
from app.models import Request, User

def resolve_req(req_id, authorized):
    req = Request.query.get(req_id)

    if not authorized:
        req.respond(current_user.id, False)
        return "A solicitação foi negada com sucesso"
    
    if req.action == 'include_user':
        new_user = User.query.get(req.requester_id)
        new_user.unlock()
        req.respond(current_user.id, "autorizado")
        return f"O usuário {new_user.full_name} foi incluído com sucesso"
    
    return "Ação não reconhecida"

