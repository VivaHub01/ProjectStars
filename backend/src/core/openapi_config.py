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
        
        openapi_schema.setdefault("components", {})
        
        openapi_schema["components"]["securitySchemes"] = {
            "UserAuth": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/login",
                        "scopes": {
                            "user": "Regular user access"
                        }
                    }
                },
                "description": "Standard user authentication"
            },
            "AdminAuth": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/admin/login",
                        "scopes": {
                            "admin": "Admin access"
                        }
                    }
                },
                "description": "Admin-level authentication"
            }
        }
        
        openapi_schema.setdefault("security", [])
        
        for path_item in openapi_schema.get("paths", {}).values():
            for operation in path_item.values():
                tags = operation.get("tags", [])
                
                if any("admin" in tag.lower() for tag in tags):
                    operation["security"] = [{"AdminAuth": ["admin"]}]
                elif any(tag.lower() in ("auth", "authentication") for tag in tags):
                    operation["security"] = [{"UserAuth": ["user"]}]
                
                if "superadmin" in operation.get("summary", "").lower():
                    operation.setdefault("description", "")
                    operation["description"] += "\n\n**Requires superadmin privileges**"
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi