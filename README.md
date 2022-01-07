# etl-music
Personal project to help me learn some data pipeline concepts. The idea of this project is to retrieve information from a personal mp3 collection, load this information on a sql table to make it possible to use it to fetch some data through spotify apis. These data collected from spotify are loaded in other sql table to make it easier to analyse it.
For this project, I used:
- **Docker-compose** for environment provisioning,
- **Python3** for data manipulation and transformation,
- **PostgreSQL** for DB,
- **Apache Airflow** for workflow/tasks management and log and
- **Apache Superset** for Data visualization.

