from db.conn import open_conn
import pandas as pd
import json

def main():
    conn = open_conn()

    df = pd.read_sql(
    '''select distinct uds.bairro, 
        translate(trim(upper(replace(replace(uds.nome_mapa,'Sr.ª', 'SENHORA'), 'US ', 'UMS '))),  
	    'áàâãäåaaaÁÂÃÄÅAAAÀéèêëeeeeeEEEÉEEÈìíîïìiiiÌÍÎÏÌIIIóôõöoooòÒÓÔÕÖOOOùúûüuuuuÙÚÛÜUUUUçÇñÑýÝ',  
	    'aaaaaaaaaAAAAAAAAAeeeeeeeeeEEEEEEEiiiiiiiiIIIIIIIIooooooooOOOOOOOOuuuuuuuuUUUUUUUUcCnNyY') as nome, 
        ST_AsGeoJSON(ST_Transform(ST_SetSRID(uds.geom,32322),4326)) as geojson 
    from public.marcelo_atendimento_unidade_saude as maus
    inner join saude.unidade_de_saude as uds
        on replace(trim(maus.desc_unidade),' PSF','') = 
        translate(trim(upper(replace(replace(uds.nome_mapa,'Sr.ª', 'SENHORA'), 'US ', 'UMS '))),  
        'áàâãäåaaaÁÂÃÄÅAAAÀéèêëeeeeeEEEÉEEÈìíîïìiiiÌÍÎÏÌIIIóôõöoooòÒÓÔÕÖOOOùúûüuuuuÙÚÛÜUUUUçÇñÑýÝ',  
        'aaaaaaaaaAAAAAAAAAeeeeeeeeeEEEEEEEiiiiiiiiIIIIIIIIooooooooOOOOOOOOuuuuuuuuUUUUUUUUcCnNyY')
    where maus.municipio = 'CURITIBA' 
        and trim(maus.bairro) <> 'BAIRRO NAO INFORMADO' 
        and trim(maus.bairro) <> 'CURITIBA'
    order by nome
    ''', conn)

    df.to_csv('data/geojson_unidades_saude_inicial.csv')
    print(df)

    #df = pd.read_csv('data/geojson_unidades_saude_inicial.csv')
    #print(df)

    features = []
    for i in range(len(df)):
        features.append({
            "type": "Feature", 
            "geometry": json.loads(df['geojson'][i]),
            "properties": {"nome": df['nome'][i]}
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open('data/geojson_unidades_saude.json', 'w') as f:
        json.dump(geojson, f)

if __name__ == '__main__':
    main()