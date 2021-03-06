# SCRIPT TO DOWNLOAD AND LOAD FEDERAL REVENUE CNPJ
# Create by: Ney Moresco
# Date: 2021-09-21
# Update: 2022-03-02

import io
import os
import time
import zipfile
import re
import requests
import pandas as pd
from sqlalchemy import create_engine

# Set Global Variables
USER = 'user_db'
PASSWORD = 'password'
SERVER_IP = 'server_ip:port' # Server IP + Port
SCHEMA = 'schema_name'

class base_cnpj:
    # Function download files
    def download_file(self, url: str, dest_file: str):
        req = requests.get(url)
        file = open(dest_file, 'wb')
        for chunk in req.iter_content(100000):
            file.write(chunk)
        file.close()
        return True

    def __init__(self, user, password, ip_postgres, schema):
        # Set Variables
        self.user = user
        self.password = password
        self.serverip = ip_postgres
        self.schema = schema
        self.files = []
        self.uploaded = []
        self.engine = None

    def get_last_update(self):
        self.HTML = requests.get('https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj')
        return self.HTML.text.split('Atualizado em')[1][36:46]

    def start_download(self):
        # Create an array with filenames and start download
        self.urls = [f'http://{i}.zip' for i in re.findall('http://(.*?).zip', self.HTML.text)][:-2]
        self.files = [x.split('/')[-1] for x in obj.urls]

        for i in self.urls:
            self.download_file(i, i.split('/')[-1])

    def psql_insert_copy(table, conn, keys, data_iter):
        import csv
        from io import StringIO
        """
        Execute SQL statement inserting data

        Parameters
        ----------
        table : pandas.io.sql.SQLTable
        conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
        keys : list of str
            Column names
        data_iter : Iterable that iterates the values to be inserted
        """
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join(['"{}"'.format(k) for k in keys])
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)

    def upload_to_postgresql(self):
        # Set layout, in order to facilitate the reading of the base a pattern was created in the first two digits, being:
        # st = string
        # cd = code
        # dt = date

        if self.engine is None:
            # Create postgresql engine 
            self.engine = create_engine(f'postgresql://{self.user}:{self.password}@{self.serverip}/postgres?options=-csearch_path%3D{self.schema}')

        layout_files = {'EMPRE': {'columns':
                                {'st_cnpj_base': [], 'st_razao_social': [], 'cd_natureza_juridica': [], 'cd_qualificacao': [],
                                    'vl_capital_social': [], 'cd_porte_empresa': [], 'st_ente_federativo': []},
                                'table_name_db': 'tb_empresa'},
                        'ESTABELE': {'columns':
                                    {'st_cnpj_base': [], 'st_cnpj_ordem': [], 'st_cnpj_dv': [], 'cd_matriz_filial': [], 'st_nome_fantasia': [], 'cd_situacao_cadastral': [],
                                    'dt_situacao_cadastral': [], 'cd_motivo_situacao_cadastral': [], 'st_cidade_exterior': [], 'cd_pais': [], 'dt_inicio_atividade': [],
                                    'cd_cnae_principal': [], 'cd_cnae_secundario': [], 'st_tipo_logradouro': [], 'st_logradouro': [], 'st_numero': [], 'st_complemento': [],
                                    'st_bairro': [], 'st_cep': [], 'st_uf': [], 'cd_municipio': [], 'st_ddd1': [], 'st_telefone1': [], 'st_ddd2': [], 'st_telefone2': [],
                                    'st_ddd_fax': [], 'st_fax': [], 'st_email': [], 'st_situacao_especial': [], 'dt_situacao_especial': []
                                    }, 'table_name_db': 'tb_estabelecimento'},
                        'SIMPLES': {'columns':
                                    {'st_cnpj_base': [], 'st_opcao_simples': [], 'dt_opcao_simples': [], 'dt_exclusao_simples': [],
                                    'st_opcao_mei': [], 'dt_opcao_mei': [], 'dt_exclusao_mei': []
                                    }, 'table_name_db': 'tb_dados_simples'},
                        'SOCIO': {'columns':
                                {'st_cnpj_base': [], 'cd_tipo': [], 'st_nome': [], 'st_cpf_cnpj': [], 'cd_qualificacao': [], 'dt_entrada': [],
                                    'cd_pais': [], 'st_representante': [], 'st_nome_representante': [], 'cd_qualificacao_representante': [], 'cd_faixa_etaria': []},
                                'table_name_db': 'tb_socio'},
                        'PAIS': {'columns': {'cd_pais': [], 'st_pais': []}, 'table_name_db': 'tb_pais'},
                        'MUNIC': {'columns': {'cd_municipio': [], 'st_municipio': []}, 'table_name_db': 'tb_municipio'},
                        'QUALS': {'columns': {'cd_qualificacao': [], 'st_qualificacao': []}, 'table_name_db': 'tb_qualificacao_socio'},
                        'NATJU': {'columns': {'cd_natureza_juridica': [], 'st_natureza_juridica': []}, 'table_name_db': 'tb_natureza_juridica'},
                        'MOTI': {'columns': {'cd_motivo_situacao_cadastral': [], 'st_motivo_situacao_cadastral': []}, 'table_name_db': 'tb_motivo_situacao_cadastral'},
                        'CNAE': {'columns': {'cd_cnae': [], 'st_cnae': []}, 'table_name_db': 'tb_cnae'}
                        }

        if self.uploaded == []:
            # List all files in path
            uploaded = []
        else:
            uploaded = self.uploaded

        # Create table with zero records
        for table in layout_files.keys():
            if sum([i.find(table) > 0 for i in uploaded]) > 0:
                continue

            df = pd.DataFrame(layout_files[table]['columns'], dtype=str)
            df.to_sql(layout_files[table]['table_name_db'], self.engine, if_exists="replace", index=False)

        for file in self.files:
            # Check loaded files
            if file in uploaded:
                continue

            temp_file = io.BytesIO()
            # Select layout from filename
            model = file.replace('.zip', '').split('.')[-1].replace('CSV', '') if file.find('SIMPLES') < 0 else 'SIMPLES'
            # Unzip file into memory
            with zipfile.ZipFile(file, 'r') as zip_ref:
                temp_file.write(zip_ref.read(zip_ref.namelist()[0]))

            # Indicator back to zero
            temp_file.seek(0)

            # Read csv's
            for chunk in pd.read_csv(temp_file, delimiter=';', header=None, chunksize=65000, names=list(layout_files[model]['columns'].keys()), iterator=True, dtype=str, encoding="ISO-8859-1"):
                # Format date columns
                for i in chunk.columns[chunk.columns.str.contains('dt_')]:
                    chunk.loc[chunk[i] == '00000000', i] = None
                    chunk.loc[chunk[i] == '0', i] = None
                    chunk[i] = pd.to_datetime(chunk[i], format='%Y%m%d', errors='coerce')

                chunk.fillna('', inplace = True)

                # Using Try for connection attempts, if the connection is lost, wait 60 seconds to retry
                try:
                    chunk.to_sql(layout_files[model]['table_name_db'], self.engine, if_exists="append", index=False, method= base_cnpj.psql_insert_copy)
                except:
                    time.sleep(60)
                    chunk.to_sql(layout_files[model]['table_name_db'], self.engine, if_exists="append", index=False, method= base_cnpj.psql_insert_copy)

            # Store processed filenames
            uploaded.append(file)
        
        self.uploaded = uploaded

    def daily_routine(self, download = True, upload = True):
        lines = '01/01/1900'
        if os.path.exists('info.txt'):
            with open('info.txt', 'r') as f:
                lines = f.readlines()

        if self.get_last_update() == lines[1]:
            return "Nothing to do!"
        else:
            if download:
                self.start_download()
            if upload:
                self.upload_to_postgresql()

            with open('info.txt', 'w') as f:
                f.write('DATE_LAST_UPDATE\n{}'.format(self.get_last_update()))

            return "Updated: {}".format(self.get_last_update())

if __name__ == '__main__':
    obj = base_cnpj(USER, PASSWORD, SERVER_IP, SCHEMA)
    print(obj.daily_routine(download = True, upload = True))