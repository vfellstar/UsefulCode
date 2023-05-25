import multiprocessing, pandas as pd, psycopg2, json, os, logging
from sqlalchemy import create_engine, sql, Column, Integer, String, Float, Date, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import sqlalchemy as db

from modules.settings.EnvSettings import Settings, GET_DATABASE_URL


class DatabaseConnection:
    log = logging.getLogger(__name__)
    database_write_lock = multiprocessing.Lock()
    
    
    
    def __init__(self) -> None:
        """
        Class that handles database connections and queries.
        """
        self.__list_of_tables = ["category", "document", "entity", "setting" ]
        self.__engine = create_engine(GET_DATABASE_URL())
        self.__connection = psycopg2.connect(GET_DATABASE_URL())
        self.__cursor = self.__connection.cursor()
        self.__metadata = db.MetaData()        
        
        # create tables
        need_to_push_changes = False
        if not db.inspect(self.__engine).has_table("category"):
            db.Table("category",
                        self.__metadata,
                        Column("id", Integer, primary_key=True),
                        Column("name", String(255), unique=True)
                        )
            need_to_push_changes = True
        if not db.inspect(self.__engine).has_table("document"):
            db.Table("document",
                        self.__metadata,
                        Column("id", Integer, primary_key=True),
                        Column("name", String(255)),
                        
                        Column("category_id", Integer, db.ForeignKey("category.id")),
                        Column("path", String(255), server_default="NONE"),
                        Column("date_uploaded", DateTime, server_default=func.now()),
                        Column("content", Text)
                        )
            need_to_push_changes = True
        if not db.inspect(self.__engine).has_table("entity"):
            db.Table("entity",
                        self.__metadata,
                        Column("id", Integer, primary_key=True),
                        Column("name", String(255)),
                        
                        Column("regex", String(255))
                    )
            need_to_push_changes = True
        if not db.inspect(self.__engine).has_table("setting"):
            db.Table("setting",
                        self.__metadata,
                        Column("id", Integer, primary_key=True),
                        Column("name", String(255), unique=True),
                        Column("value", Text, nullable=False),
                        Column("data_type", String(255), nullable=False)
                        )
            need_to_push_changes = True
        if not db.inspect(self.__engine).has_table("active_entities"):
            db.Table("active_entities", 
                        self.__metadata,
                        Column("id", Integer, primary_key=True),
                        Column("entity_id", Integer, db.ForeignKey("entity.id")),
                        Column("active", Boolean, server_default="True")
                        )
            need_to_push_changes = True
            
        if need_to_push_changes == True:
            self.__create_necessary_tables()        

    def query_database_as_df(self, query):
        with self.__engine.connect().execution_options(autocommit=True) as connection:
            query = connection.execute(sql.text(query))
        df = pd.DataFrame(query.fetchall())
        
        return df
    
    def query_database_raw(self, query):
        try:
            self.__cursor = self.__connection.cursor()
            self.__cursor.execute(query)
            return self.__cursor.fetchall()
        except Exception as e:
            self.__connection.rollback()
            return str(e)
        finally:
            self.__cursor.close()

    def alter_db(self, query):
        try:
            self.__cursor = self.__connection.cursor()
            self.__cursor.execute(query)
            self.__connection.commit()
            return True
        except BaseException as e:
            self.__connection.rollback()
            return str(e)
        finally:
            self.__cursor.close()
                
    def get_all_tables(self):
        sql_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        result = self.query_database_raw(sql_query)
        lst = []
        for item in result:
            lst.append(item[0])
        return lst
        
    
# Completed private methods
    def __had_all_tables(self, tables_in_db):
        for table in self.__list_of_tables:
            if table not in tables_in_db:
                return False
        return True
        
    def __create_necessary_tables(self):
        tables_in_db = self.get_all_tables()
        if self.__had_all_tables(tables_in_db) or len(tables_in_db) == 0:
            DatabaseConnection.log.info(f"Not all tables in database. Creating tables: {self.__list_of_tables}.")
            self.__metadata.create_all(self.__engine)
            DatabaseConnection.log.info(f"Setup Complete. Created the tables: {self.get_all_tables()}.")
        else:
            DatabaseConnection.log.info(f"All necessary tables exist in database... Starting application.")
        