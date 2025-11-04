from fastapi import FastAPI
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from instrument import setup_instrumentation, get_redis_client

app = FastAPI()

# SQLAlchemy async engine setup - must be created before instrumentation
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/myapp"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Setup instrumentation - pass the engine so SQL queries are traced
tracer, meter, logger = setup_instrumentation(app, engine=engine)
redis = get_redis_client()


@app.get("/")
def read_root():
    with tracer.start_as_current_span("read_root") as span:
        redis.set("name", "basit")
        span.set_attribute("key", "name")
        span.set_attribute("value", "basit")
    return {"message": "Hello, World!"}


@app.get("/db-test")
async def db_test():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            return {"db_test": row[0] if row else None}


@app.get("/httpx-test")
async def httpx_test():
    try:
        with tracer.start_as_current_span("httpx-test") as span:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://jsonplaceholders.typicode.com/posts")
                return response.json()
    except Exception as e:
        logger.error(f"Error in httpx-test: {e}")
        return {"error": str(e)}


@app.get("/logging-test")
def logging_test():
    logger.info("Hello, World!")
    # logger.warning("Warning!")
    # logger.error("Error!")
    # logger.critical("Critical!")
    return {"message": "Logging test"}


@app.get("/favorites")
def get_favorites(username: str):
    with tracer.start_as_current_span("get_favorites") as span:
        span.set_attribute("username", username)

        key = f"user:{username}:favorite"

        favorites = redis.get(key)
        if favorites:
            # Assuming favorites are stored as JSON string
            import json

            try:
                favorites_list = json.loads(favorites)
                return {"username": username, "favorites": favorites_list}
            except json.JSONDecodeError:
                return {
                    "username": username,
                    "favorites": [],
                    "error": "Invalid data format",
                }
        else:
            return {"username": username, "favorites": []}


def main():
    print("Hello from py-instrument!")


if __name__ == "__main__":
    main()
