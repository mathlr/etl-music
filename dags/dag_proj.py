from airflow import DAG
from datetime import datetime,timedelta

from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy import DummyOperator

import os
import mp3scrape
import reqspotify

dag_args={
    'owner':'matheus',
    'depends_on_past':False,
    'email':'',
    'email_on_failure':False,
    'email_on_retry':False,
    'retries':0,
    'retry_delay':timedelta(minutes=1)
}

PATHFILES = os.getcwd()+'/files'

def scrape_func():
    st = mp3scrape.scrape_folder(PATHFILES,True)
    return 0

def write_scrape():
    # INITIALIZE POSTGRES HOOK
    pg_hook= PostgresHook(postgres_conn_id ='postgres_conn',schema='airflow')
    connection=pg_hook.get_conn()
    cursor=connection.cursor()
    # CLEAR TABLE
    truncate="TRUNCATE TABLE t_scrap_dl;"
    cursor.execute(truncate)
    # LOAD TABLE FROM FILE
    path=PATHFILES+'/scraped_data.csv'
    copy="COPY t_scrap_dl FROM STDIN DELIMITER ',' CSV HEADER;"
    with open(path,'rb') as csv_file:
        cursor.copy_expert(copy,csv_file)
    commit="COMMIT;"
    cursor.execute(commit)

    return 0

def artist_func():
    import pandas as pd

    # FILE WITH SPOTIFY CREDENTIALS SEPARATED BY COMMA
    for line in open(PATHFILES+'/spotify_cred.txt'):
        (CLIENT_ID,CLIENT_SECRET) = line.split(',')
    # LOAD DATA FROM STAGED
    mdf = pd.read_csv(PATHFILES+'/scraped_data.csv')
    # TRANSFORMATION - DELETE DUPLICATES
    artists=mdf['artist'].str.lower().unique()
    # LISTS INITIALIZATION
    oname=[]
    name=[]
    pop=[]
    gen=[]
    acc=[]
    # GET TOKEN TO SPOTIFY API
    token=reqspotify.get_cred(CLIENT_ID,CLIENT_SECRET)
    # LOOP IN ARTISTS FROM STAGED
    for art in artists:
        print(art)
        req=reqspotify.search_req('',art,'','artist',token)
        # TRY AGAIN IF TOKEN EXPIRED
        if req.status_code == 403:
            token=reqspotify.get_cred(CLIENT_ID,CLIENT_SECRET)
            req=reqspotify.search_req('',art,'','artist',token)
        req=req.json()
        len_r=len(req['artists']['items'])
        # TRY AGAIN IN QUICK MODE IF NO RESULT FOUND
        if len_r == 0:
            req=reqspotify.search_req('',art,'','artist',token,True)
            req=req.json()
            len_r=len(req['artists']['items'])
        oname.append(art)
        # PRIORITIZE FIRST RESULT + TRANSFORMATION
        name.append(req['artists']['items'][0]['name'] if len_r > 0 else 'N/F')
        pop.append(req['artists']['items'][0]['popularity'] if len_r > 0 else 0)
        gen.append(str(req['artists']['items'][0]['genres']).replace('[','{').replace(']','}').replace("'",'') if len_r > 0 else '')
        acc.append(False if req['artists']['total'] > 1 else True)
    # CREATE DATAFRAME WITH RESULTS AND SAVE FILE
    dartists={'oname':oname,'name':name,'popularity':pop,'genres':gen,'accuracy':acc}
    adf=pd.DataFrame(dartists)
    adf.to_csv(PATHFILES+'/artist_data.csv',index=False)

    return 0

def write_artist():
    # INITIALIZE POSTGRES HOOK
    pg_hook= PostgresHook(postgres_conn_id ='postgres_conn',schema='airflow')
    connection=pg_hook.get_conn()
    cursor=connection.cursor()
    # CLEAR TABLE
    truncate="TRUNCATE TABLE t_artist;"
    cursor.execute(truncate)
    # LOAD TABLE FROM FILE
    path=PATHFILES+'/artist_data.csv'
    copy="COPY t_artist FROM STDIN DELIMITER ',' CSV HEADER;"
    with open(path,'rb') as csv_file:
        cursor.copy_expert(copy,csv_file)
    commit="COMMIT;"
    cursor.execute(commit)

    return 0

with  DAG('artist_etl',default_args=dag_args,start_date=datetime(2022,1,1),schedule_interval="@once",catchup=False) as dag:
    
    scrape_folder = PythonOperator(
        task_id="scrape_folder",
        python_callable=scrape_func
    )

    create_scrape_db = PostgresOperator(
        task_id='create_scrape_db',
        postgres_conn_id='postgres_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS t_scrap_dl (
                id INT,
                timestamp TIMESTAMP,
                album TEXT,
                albumartist TEXT,
                artist TEXT,
                audio_offset INT,
                bitrate INT,
                channels INT,
                comment TEXT,
                composer TEXT,
                disc TEXT,
                disc_total TEXT,
                duration DOUBLE PRECISION,
                extra TEXT,
                filesize INT,
                genre TEXT,
                samplerate INT,
                title TEXT,
                track TEXT,
                track_total TEXT,
                year TEXT,
                PRIMARY KEY (id, timestamp)
            );
        """
    )

    write_scrape = PythonOperator(
        task_id='write_scrape',
        python_callable=write_scrape
    )

    artists_info = PythonOperator(
        task_id='artists_info',
        python_callable=artist_func
    )

    create_artist_db = PostgresOperator(
        task_id='create_artist_db',
        postgres_conn_id='postgres_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS t_artist (
                oname TEXT,
                name TEXT,
                popularity INT,
                genres TEXT[],
                accuracy BOOLEAN,
                PRIMARY KEY( oname, name )
            );
        """
    )

    write_artist = PythonOperator(
        task_id='write_artist',
        python_callable=write_artist
    )

    start=DummyOperator(
        task_id='Start'
    )

    oetl=DummyOperator(
        task_id='OTHER-ETLs'
    )

start.set_downstream(scrape_folder)
scrape_folder.set_downstream(create_scrape_db)
create_scrape_db.set_downstream(write_scrape)
write_scrape.set_downstream(oetl)
write_scrape.set_downstream(artists_info)
artists_info.set_downstream(create_artist_db)
create_artist_db.set_downstream(write_artist)