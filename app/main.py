from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextlib import asynccontextmanager
from app.config import CORS_ORIGINS
from app.utils.logger import logger
from app.database.db import check_db_health, Base, SessionLocal, get_active_engine
from app.services.feedback_service import FeedbackService
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Lifespan event handler initializing DB tables on application startup."""
    try:
        active_engine = get_active_engine()
        Base.metadata.create_all(bind=active_engine)
        logger.info(f"Database initialized successfully on startup using engine: {active_engine.dialect.name}")
    except Exception as e:
        logger.error(f"Startup database initialization error: {e}")
    yield

# Initialize FastAPI application instance
app = FastAPI(
    title="ProductIQ API",
    description="AI-Driven Product Feedback Intelligence & Developer Workflow Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API v1 Router
app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "ok", "service": "ProductIQ API", "version": "1.0.0"}

@app.get("/health")
def health_root():
    return {"status": "ok", "service": "ProductIQ API"}


def run_demo(session):
    feedback_text = "The login page freezes after clicking Sign In."
    service = FeedbackService(session=session)

    try:
        result = service.process_and_store_feedback(raw_text=feedback_text, platform="Web")
        fb = result["feedback"]
        dup = result["duplicate_result"]
        rm = result["roadmap"]
        tasks = result["tasks"]

        print("=" * 50)
        print("PRODUCTIQ FEEDBACK")
        print("=" * 50)
        print(f"Original:\n{fb.original_text}\n")
        print(f"Feedback Type:\n{fb.feedback_type}\n")
        print(f"Category:\n{fb.category}\n")
        print(f"Subcategory:\n{fb.subcategory}\n")
        print(f"Severity:\n{fb.severity}\n")
        print(f"Priority:\n{fb.priority}\n")
        print(f"Recommended Action:\n{fb.recommended_action}\n")

        print("=" * 50)
        print("DUPLICATE ANALYSIS")
        print("=" * 50)
        print(f"Duplicate:\n{'Yes' if dup.is_duplicate else 'No'}\n")
        print(f"Similarity:\n{dup.similarity_score:.2f}\n")

        if rm and tasks:
            from app.services.task_workflow_service import TaskWorkflowService
            workflow = TaskWorkflowService(session=session)

            print("=" * 50)
            print("PRODUCTIQ DEVELOPER WORKFLOW")
            print("=" * 50)
            print(f"Feedback:\n{fb.original_text}\n")
            print(f"Roadmap:\n{rm.title}\n")
            print(f"Initial Progress:\n{rm.progress}%\n")
            print(f"Status:\n{rm.status}\n")

            # Update tasks sequentially
            last_res = None
            for idx, task in enumerate(tasks, start=1):
                print("-" * 50)
                print(f"TASK {idx} UPDATE: {task.title}")
                print("-" * 50)

                if idx == len(tasks):
                    # Intermediate update to Approved (Testing)
                    r_test = workflow.update_task_progress_and_status(task.id, update={"progress": 100, "status": "Approved"})
                    print(f"Task {idx} Progress: 100%, Status: Approved")
                    print(f"Roadmap Progress: {r_test['roadmap'].progress}%, Status: {r_test['roadmap'].status}\n")

                    # Final update to Resolved
                    print("-" * 50)
                    print("FINAL RESOLUTION UPDATE")
                    print("-" * 50)
                    last_res = workflow.update_task_progress_and_status(task.id, update={"status": "Resolved"})
                else:
                    last_res = workflow.update_task_progress_and_status(task.id, update={"progress": 100, "status": "Resolved"})

                print(f"Task {idx} Progress: 100%, Status: {last_res['task'].status}")
                print(f"Roadmap Progress: {last_res['roadmap'].progress}%, Status: {last_res['roadmap'].status}\n")

            print("-" * 50)
            print("FINAL PIPELINE STATE")
            print("-" * 50)
            if last_res:
                print(f"Roadmap Status: {last_res['roadmap'].status}")
                print(f"Roadmap Progress: {last_res['roadmap'].progress}%")
                print(f"Feedback Status: {last_res['feedback'].status}")
                if last_res['notification']:
                    print(f"Notification Created: Yes")
                    print(f"Message: {last_res['notification'].message}")
            print("=" * 50)

    except Exception as err:
        logger.error(f"Demo execution failed: {err}")
        print(f"Demo failed: {err}")


def main():
    logger.info("ProductIQ Phase 4 Pipeline initialized.")
    db_status = check_db_health()
    if db_status["connected"]:
        logger.info(f"Database health check passed [{db_status['database']}].")
        session = SessionLocal()
        try:
            run_demo(session)
        finally:
            session.close()
    else:
        logger.warning("PostgreSQL unavailable. Running demo in-memory with SQLite.")
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            run_demo(session)
        finally:
            session.close()


if __name__ == "__main__":
    main()

