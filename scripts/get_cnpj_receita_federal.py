# SCRIPT TO DOWNLOAD AND LOAD FEDERAL REVENUE CNPJ
# Create by: Ney Moresco
# Date: 2021-09-21

# Import packages
from sqlalchemy import create_engine
import pandas as pd
import os
import zipfile
import time
import io

# Function download files
def download_file(url: str, dest_file: str):
    import requests
    req = requests.get(url)
    file = open(dest_file, 'wb')
    for chunk in req.iter_content(100000):
        file.write(chunk)
    file.close()
    return True

# Set Variables
user = 'username'
password = 'password_postgres'
serverip = 'ip_postgres'
schema = 'name_of_schema'

# Create postgresql engine 
engine = create_engine(f'postgresql://{user}:{password}@{serverip}/postgres?options=-csearch_path%3D{schema}')

# Set URL and Path
url = 'http://200.152.38.155/CNPJ/'
path = 'zip_files/'

# Create an array with filenames and start download (EMPRESAS)
files = [f'K3241.K03200Y{i}.D10814.EMPRECSV.zip' for i in range(10)]
for i in files:
    download_file(url + i, path + i)

# Create an array with filenames and start download (ESTABELECIMENTOS)
files = [f'K3241.K03200Y{i}.D10814.ESTABELE.zip' for i in range(10)]
for i in files:
    download_file(url + i, path + i)

# Create an array with filenames and start download (Auxiliary bases)
files = ['F.K03200$Z.D10814.QUALSCSV.zip', 'F.K03200$Z.D10814.MOTICSV.zip', 'F.K03200$Z.D10814.CNAECSV.zip', 'F.K03200$W.SIMPLES.CSV.D10814.zip', 'F.K03200$Z.D10814.MUNICCSV.zip',
         'F.K03200$Z.D10814.NATJUCSV.zip', 'F.K03200$Z.D10814.PAISCSV.zip']
for i in files:
    download_file(url + i, path + i)

# Definindo Layout das bases para carga no Banco de dados
# Set layout, in order to facilitate the reading of the base a pattern was created in the first two digits, being:
# st = string
# cd = code
# dt = date
layout_files = {'EMPRE': {'columns':
                          {'st_cnpj_base': str, 'st_razao_social': str, 'cd_natureza_juridica': str, 'cd_qualificacao': str,
                              'vl_capital_social': str, 'cd_porte_empresa': str, 'st_ente_federativo': str},
                          'table_name_db': 'tb_empresa'},
                'ESTABELE': {'columns':
                             {'st_cnpj_base': str, 'st_cnpj_ordem': str, 'st_cnpj_dv': str, 'cd_matriz_filial': str, 'st_nome_fantasia': str, 'cd_situacao_cadastral': str,
                              'dt_situacao_cadastral': str, 'cd_motivo_situacao_cadastral': str, 'st_cidade_exterior': str, 'cd_pais': str, 'dt_inicio_atividade': str,
                              'cd_cnae_principal': str, 'cd_cnae_secundario': str, 'st_tipo_logradouro': str, 'st_logradouro': str, 'st_numero': str, 'st_complemento': str,
                              'st_bairro': str, 'st_cep': str, 'st_uf': str, 'cd_municipio': str, 'st_ddd1': str, 'st_telefone1': str, 'st_ddd2': str, 'st_telefone2': str,
                              'st_ddd_fax': str, 'st_fax': str, 'st_email': str, 'st_situacao_especial': str, 'dt_situacao_especial': str
                              }, 'table_name_db': 'tb_estabelecimento'},
                'SIMPLES': {'columns':
                            {'st_cnpj_base': str, 'st_opcao_simples': str, 'dt_opcao_simples': str, 'dt_exclusao_simples': str,
                             'st_opcao_mei': str, 'dt_opcao_mei': str, 'dt_exclusao_mei': str
                             }, 'table_name_db': 'tb_dados_simples'},
                'SOCIO': {'columns':
                           {'st_cnpj_base': str, 'cd_tipo': str, 'st_nome': str, 'st_cpf_cnpj': str, 'cd_qualificacao': str, 'dt_entrada': str,
                            'cd_pais': str, 'st_representante': str, 'st_nome_representante': str, 'cd_qualificacao_representante': str, 'cd_faixa_etaria': str},
                          'table_name_db': 'tb_socio'},
                'PAIS': {'columns': {'cd_pais': str, 'st_pais': str}, 'table_name_db': 'tb_pais'},
                'MUNIC': {'columns': {'cd_municipio': str, 'st_municipio': str}, 'table_name_db': 'tb_municipio'},
                'QUALS': {'columns': {'cd_qualificacao': str, 'st_qualificacao': str}, 'table_name_db': 'tb_qualificacao_socio'},
                'NATJU': {'columns': {'cd_natureza_juridica': str, 'st_natureza_juridica': str}, 'table_name_db': 'tb_natureza_juridica'},
                'MOTI': {'columns': {'cd_motivo_situacao_cadastral': str, 'st_motivo_situacao_cadastral': str}, 'table_name_db': 'tb_motivo_situacao_cadastral'},
                'CNAE': {'columns': {'cd_cnae': str, 'st_cnae': str}, 'table_name_db': 'tb_cnae'}
                }

# List all files in path
files = os.listdir(path)
uploaded = []

for file in files:
    # Check loaded files
    if file in uploaded:
        continue

    temp_file = io.BytesIO()

    # Select layout from filename
    model = file.replace('.zip', '').split('.')[-1].replace('CSV', '') if file.find('SIMPLES') < 0 else 'SIMPLES'

    # Unzip file into memory
    with zipfile.ZipFile(path + file, 'r') as zip_ref:
        temp_file.write(zip_ref.read(zip_ref.namelist()[0]))

    # Indicator back to zero
    temp_file.seek(0)

    # Read csv's
    for chunk in pd.read_csv(temp_file, delimiter=';', header=None, chunksize=65000, names=list(layout_files[model]['columns'].keys()), iterator=True, dtype=str, encoding="ISO-8859-1"):
        # Format date columns
        for i in chunk.columns[chunk.columns.str.contains('dt_')]:
            chunk.loc[chunk[i] == '00000000', i] = None
            chunk.loc[chunk[i] == '0', i] = None
            chunk[i] = pd.to_datetime(
                chunk[i], format='%Y%m%d', errors='coerce')

        # Using Try for connection attempts, if the connection is lost, wait 60 seconds to retry
        try:
            chunk.to_sql(layout_files[model]['table_name_db'],
                         engine, if_exists="append", index=False)
        except:
            time.sleep(60)
            chunk.to_sql(layout_files[model]['table_name_db'],
                         engine, if_exists="append", index=False)

    # Store processed filenames
    uploaded.append(file)
