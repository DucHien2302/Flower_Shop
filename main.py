from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db import engine, Base
from routers import users, flowertype, categories, products, flowers, informations

app = FastAPI()

# --- Cấu hình CORS ---
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://your-frontend-domain.com",
    "http://192.168.10.132:5173",
    "http://192.168.1.194:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Kết thúc cấu hình CORS ---

# Khởi tạo cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Đăng ký router với prefix và tags
app.include_router(users.router, tags=["Users"])
app.include_router(categories.router,tags=["Categories"])
app.include_router(flowertype.router, tags=["Flower Types"])
app.include_router(products.router, tags=["Products"])
app.include_router(flowers.router, tags=["Flowers"])
app.include_router(informations.router, tags=["Informations"])

# (Optional) Route gốc để kiểm tra nhanh
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "API is running with CORS enabled!"}