from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.data_upload import DataUploadService
from app.services.db_explorer import DBExplorerService
from app.services.query_generator import QueryGeneratorService
from app.services.nlp_processor import NLPProcessor
from app.database.mysql_manager import MySQLManager
from app.database.mongo_manager import MongoManager
from app.config import settings
from pydantic import BaseModel

router = APIRouter()

mysql_manager = MySQLManager(settings.mysql_connection_string)
mongo_manager = MongoManager(settings.mongo_connection_string, settings.mongo_db_name)
data_upload_service = DataUploadService(mysql_manager, mongo_manager)
db_explorer_service = DBExplorerService(mysql_manager, mongo_manager)
query_generator_service = QueryGeneratorService()
nlp_processor = NLPProcessor()


@router.get("/")
async def root():
    return {"message": "Welcome to ChatDB"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), db_type: str = "mysql", table_name: str = None
):
    if not table_name:
        table_name = file.filename.split(".")[0]
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    if db_type == "mysql":
        data_upload_service.upload_to_mysql(file_path, table_name)
    elif db_type == "mongodb":
        data_upload_service.upload_to_mongo(file_path, table_name)
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")

    return {"message": f"File uploaded successfully to {db_type}"}


@router.get("/explore")
async def explore_database(db_type: str = "mysql"):
    if db_type == "mysql":
        tables = db_explorer_service.get_mysql_tables()
        return {"tables": tables}
    elif db_type == "mongodb":
        collections = db_explorer_service.get_mongo_collections()
        return {"collections": collections}
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")


@router.get("/sample-data")
async def get_sample_data(db_type: str, table_name: str):
    if db_type == "mysql":
        return db_explorer_service.get_mysql_sample_data(table_name)
    elif db_type == "mongodb":
        return db_explorer_service.get_mongo_sample_data(table_name)
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")


@router.get("/sample-queries")
async def get_sample_queries(db_type: str, table_name: str):
    if db_type == "mysql":
        columns = db_explorer_service.get_mysql_columns(table_name)
    elif db_type == "mongodb":
        columns = db_explorer_service.get_mongo_fields(table_name)
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")

    queries = query_generator_service.generate_sample_queries(table_name, columns)
    return {"sample_queries": queries}


class NLQueryRequest(BaseModel):
    query: str
    db_type: str
    table_name: str


@router.post("/natural-language-query")
async def process_nl_query(request: NLQueryRequest):
    processed_query = nlp_processor.process_query(request.query)
    pattern = nlp_processor.match_query_pattern(processed_query)

    if pattern:
        if request.db_type == "mysql":
            columns = db_explorer_service.get_mysql_columns(request.table_name)
        elif request.db_type == "mongodb":
            columns = db_explorer_service.get_mongo_fields(request.table_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid database type")

        sql_query = nlp_processor.generate_sql_query(
            pattern, request.table_name, columns
        )
        return {"matched_pattern": pattern, "generated_query": sql_query}
    else:
        return {"message": "No matching query pattern found"}


class QueryRequest(BaseModel):
    query: str
    db_type: str
    table_name: str


@router.post("/execute-query")
async def execute_query(request: QueryRequest):
    if request.db_type == "mysql":
        result = mysql_manager.execute_query(request.query)
    elif request.db_type == "mongodb":
        result = mongo_manager.execute_query(request.table_name, eval(request.query))
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")

    return {"result": result}
