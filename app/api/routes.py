from enum import Enum
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.data_upload import DataUploadService
from app.services.db_explorer import DBExplorerService
from app.services.query_generator import QueryGeneratorService
from app.services.nlp_processor import NLPProcessor, DatabaseType
from app.database.mysql_manager import MySQLManager
from app.database.mongo_manager import MongoManager
from app.config import settings
from pydantic import BaseModel
from typing import Optional
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

router = APIRouter()

mysql_manager = MySQLManager(settings.mysql_connection_string)
mongo_manager = MongoManager(settings.mongo_connection_string)
data_upload_service = DataUploadService(mysql_manager, mongo_manager)
db_explorer_service = DBExplorerService(mysql_manager, mongo_manager)
query_generator_service = QueryGeneratorService()
nlp_processor = NLPProcessor()

logger = logging.getLogger(__name__)
logger.info(f"MySQL connection string: {settings.mysql_connection_string}")


@router.get("/")
async def root():
    return {"message": "Welcome to ChatDB"}


class DatabaseUploadRequest(BaseModel):
    db_type: str
    database_name: Optional[str] = None
    table_name: str


@router.post("/upload")
async def upload_file(
    db_type: str = Form(...),
    table_name: str = Form(...),
    database_name: str = Form(...),
    file: UploadFile = File(...),
):
    if not database_name:
        raise HTTPException(status_code=400, detail="Database name is required")

    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        if db_type == "mysql":
            result = data_upload_service.upload_to_mysql(
                file_path, table_name, database_name
            )
        elif db_type == "mongodb":
            result = data_upload_service.upload_to_mongo(
                file_path, table_name, database_name
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid database type")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/explore")
async def explore_database(db_type: str = "mysql", database_name: Optional[str] = None):
    try:
        if db_type == "mysql":
            tables = db_explorer_service.get_mysql_tables(database_name)
            return {"tables": tables}
        elif db_type == "mongodb":
            collections = db_explorer_service.get_mongo_collections(database_name)
            return {"collections": collections}
        else:
            raise HTTPException(status_code=400, detail="Invalid database type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-data")
async def get_sample_data(
    db_type: str, table_name: str, database_name: Optional[str] = None
):
    if db_type == "mysql":
        return db_explorer_service.get_mysql_sample_data(
            table_name, database_name=database_name
        )
    elif db_type == "mongodb":
        return db_explorer_service.get_mongo_sample_data(
            table_name, database_name=database_name
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")


@router.get("/sample-queries")
async def get_sample_queries(
    db_type: str,
    table_name: str,
    construct: Optional[str] = None,
    database_name: Optional[str] = None,
):
    try:
        available_tables = db_explorer_service.get_all_tables_and_columns(
            db_type, database_name=database_name
        )
        print(available_tables)
        if db_type == "mysql":
            columns = db_explorer_service.get_mysql_columns(table_name, database_name)
        elif db_type == "mongodb":
            columns = db_explorer_service.get_mongo_fields(table_name, database_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid database type")

        # If construct is specified, generate queries for that specific construct
        if construct:
            queries = nlp_processor.get_queries_by_construct(
                construct, table_name, columns, DatabaseType(db_type), available_tables
            )
            return {
                "sample_queries": [
                    {
                        "natural_language": f"Query using {construct}",
                        f"{db_type}_query": query,
                    }
                    for query in queries
                ]
            }

        # Otherwise, generate a variety of sample queries
        queries = query_generator_service.generate_sample_queries(
            table_name, columns, db_type=db_type, available_tables=available_tables
        )
        return {"sample_queries": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NLQueryRequest(BaseModel):
    query: str
    db_type: str
    table_name: str
    database_name: Optional[str] = None


@router.post("/natural-language-query")
async def process_nl_query(request: NLQueryRequest):
    logging.info(f"Received NLQueryRequest: {request}")
    try:
        processed_query = nlp_processor.process_query(request.query)
        logging.info(f"Processed query: {processed_query}")
        pattern = nlp_processor.match_query_pattern(processed_query)
        logging.info(f"Matched pattern: {pattern}")

        if pattern:
            available_tables = db_explorer_service.get_all_tables_and_columns(
                request.db_type, database_name=request.database_name
            )

            if request.db_type == "mysql":
                columns = db_explorer_service.get_mysql_columns(
                    request.table_name, request.database_name
                )
            elif request.db_type == "mongodb":
                columns = db_explorer_service.get_mongo_fields(
                    request.table_name, request.database_name
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid database type")

            generated_query = nlp_processor.generate_query(
                pattern,
                request.table_name,
                columns,
                request.db_type,
                available_tables,
            )

            logging.info(f"Generated query: {generated_query}")
            return {
                "matched_pattern": pattern,
                "generated_query": generated_query,
                "db_type": request.db_type,
            }
        else:
            return {"message": "No matching query pattern found"}
    except Exception as e:
        logging.error(f"Error in process_nl_query: {str(e)}, request: {request}")
        raise HTTPException(status_code=500, detail=str(e))


class QueryRequest(BaseModel):
    query: str
    db_type: str
    table_name: str
    database_name: Optional[str] = None


@router.post("/execute-query")
async def execute_query(request: QueryRequest):
    if request.db_type == "mysql":
        result = mysql_manager.execute_query(
            request.query, database_name=request.database_name
        )
    elif request.db_type == "mongodb":
        result = mongo_manager.execute_query(
            request.table_name, eval(request.query), database_name=request.database_name
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")

    return {"result": result}
