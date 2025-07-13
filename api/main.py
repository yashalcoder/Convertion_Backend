from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import image  # import your route file
from mangum import Mangum  # allows FastAPI to run on Vercel

app = FastAPI(
    title="Image Conversion API",
    version="1.0.0",
    description="Upload JPG image and get a PNG download"
)

# Allow frontend (Next.js) to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # allow all for now; in prod, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}

# Include your image routes (you can also include video routes later)
app.include_router(image.router)


# For Vercel to recognize it as a serverless function
handler = Mangum(app)
