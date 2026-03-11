from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.emp_endpoints import router as emp_router
from routes.assets_endpoints import router as asset_router
from routes.master_endpoints import router as master_router
from routes.allocation_endpoints import router as allocation_router
from routes.auth_endpoints import router as auth_router
from routes.notification_endpoints import router as notification_router

import sys
print(sys.path) 
app = FastAPI(
    title="AMS API",
    description="Asset Management System API",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000", #  frontend port of NextJS
    "*"                      # Allows all origins 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emp_router, tags=["Employees"])
app.include_router(asset_router, tags=["Assets"])
app.include_router(master_router)
app.include_router(allocation_router, tags=["Allocations"])
app.include_router(auth_router)
app.include_router(notification_router, tags=["Notifications"])

@app.get("/")
async def root():
    return {"message": "Welcome to AMS API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
