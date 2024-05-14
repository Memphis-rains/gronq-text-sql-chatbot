from django.shortcuts import render
from django.http import JsonResponse
from groq import Groq
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re
import psycopg2
from schema_parcer import get_schema_data
from difflib import SequenceMatcher
def home(request):
    return render(request,"home.html")
                  
client = Groq(
    api_key="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",
)


def check_query_alias_from_error(error_message):
    error_column = error_message.split('column')
    if '.' in error_column[1].split(' ')[1]:
        print("alias wali hai")
        return error_column[1]
    return None
 

def similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()
def classify_error(error_message):
    if "column" in error_message.lower():
        return "column"
    elif "relation" in error_message.lower():
        return "table"
    print('classify_error == ', error_message)

    
similarity_score_list = []
MAX_TRIES = 4

def query_corrector(query, error_message):
    db_schema = get_schema_data("demoDB", "postgres", "sapan", 'localhost', '5432')
    error_type = classify_error(error_message)
    
    if error_type == "column":
        error_column = check_query_alias_from_error(error_message)
        if error_column is None:
            error_column = error_message.split('"')[1]
            alias=""
        else:
            alias,error_column = error_column.split(' ')[1].split('.')
    
        corrected_query = query
        similarity_score_list = []
        for table_name, table_columns in db_schema.items():
            for j in table_columns:
                similarity_score = round(similarity(j, error_column), 2)
                similarity_score_list.append((j, similarity_score))

        if similarity_score_list:
            most_similar_column, max_similarity = max(similarity_score_list, key=lambda x: x[1])
            print(most_similar_column, 'most_similar_column@@@@@@@@@@@@@@@@@@@@@@@@@')
            # replacing the column
            new_q = []
            for item in query.split(' '):
                if item == error_column:
                    new_q.append(alias+'.'+most_similar_column)
                else:
                    lst = item.split('.')
                    print('!!!!!!!!!', lst, error_column, alias)
                    if len(lst) > 1  and lst[0] == alias and lst[1] == error_column:                  
                       new_q.append(alias+'.'+most_similar_column)
                    else:
                        new_q.append(item)
            
            corrected_query = ' '.join(new_q)
        print("Corrected Query:", corrected_query)
        return corrected_query

    elif error_type == "table":
        try:
            error_table = error_message.split('"')[1]
        except IndexError:
            print("Error: Unable to extract error table from error message.")
            return None
        
        corrected_query = query
        print("Error type:", error_type, "Error table:", error_table)

        similarity_score_list = []
        for table_name in db_schema.keys():
            similarity_score = round(similarity(table_name, error_table), 2)
            similarity_score_list.append((table_name, similarity_score))

        if similarity_score_list:
            most_similar_table, max_similarity = max(similarity_score_list, key=lambda x: x[1])

            # replacing the table
            corrected_query = query.replace(error_table, most_similar_table)
            print("**********************\nCorrected Query:", corrected_query)
            return corrected_query

    return None


def execute_query(sql_query, tries=0):
    MAX_TRIES = 10
    successful = False
    response = None
    while tries < MAX_TRIES and not successful:
        try:
            # Connect to your PostgreSQL database
            conn = psycopg2.connect(
                dbname="demoDB",
                user="postgres",
                password="sapan",
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute(sql_query)

            query_response = cursor.fetchall()
            cursor.close()
            conn.close()

            response  = {"result": query_response, "error": None}
            successful = True
        except Exception as error:
            print("\n\nTrying SQL query: === ", tries, sql_query)
            print("Error: === ", error, '=====')
            # import pdb;pdb.set_trace()
            sql_query = sql_query.replace('\n', ' ')
            sql_query = query_corrector(sql_query, str(error))
            
            tries += 1
    return response






@api_view(['GET'])
def generate_groq_query(request):
    schema = request.GET.get('schema')
    prompt = request.GET.get('prompt')
    
    # Generate SQL query using Groq
    client = Groq(api_key="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")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Write an optimised SQL query to answer this question based on the schema {schema}: {prompt}. If the prompt is not related to generating a SQL query for the provided schema,then respond ' Baraber prompt de bhai!!!' and dot put any other .",
            }
        ],
        model="llama3-70b-8192",
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    # Extract SQL query from Groq response
    sql_query = "".join([chunk.choices[0].delta.content or "" for chunk in chat_completion if chunk.choices[0].delta.content is not None])
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, sql_query, re.DOTALL)
    
    if matches:
        query = matches[0].strip()
        query=query.replace('sql','')
        output=execute_query(query)
        # output=1
        return Response({"sql_query": query,"output":output})
    else:
        return Response({"sql_query": "sql query not fount"})