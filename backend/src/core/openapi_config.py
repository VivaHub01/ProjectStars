from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def setup_openapi_config(app: FastAPI):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="Your API",
            version="1.0.0",
            routes=app.routes,
        )
        
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        
        openapi_schema["components"]["securitySchemes"] = {
            "UserAuth": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/auth/login",
                        "scopes": {
                            "user": "Regular user access"
                        }
                    }
                }
            },
            "AdminAuth": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/auth/admin/login",
                        "scopes": {
                            "admin": "Admin access"
                        }
                    }
                }
            }
        }
        
        if "paths" not in openapi_schema:
            openapi_schema["paths"] = {}
        
        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if "tags" in operation:
                    if any("admin" in tag.lower() for tag in operation["tags"]):
                        operation["security"] = [{"AdminAuth": ["admin"]}]
                    elif any("auth" in tag.lower() for tag in operation["tags"]):
                        operation["security"] = [{"UserAuth": ["user"]}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi