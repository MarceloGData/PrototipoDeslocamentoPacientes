from db.conn import open_conn
import pandas as pd
import json

def main():
    conn = open_conn()

    df = pd.read_sql('''
    select 
        translate(replace(trim(nome), 'CIDADE INDUSTRIAL DE CURITIBA', 'CIC'),  
            'áàâãäåaaaÁÂÃÄÅAAAÀéèêëeeeeeÊEEEÉEEÈìíîïìiiiÌÍÎÏÌIIIóôõöoooòÒÓÔÕÖOOOùúûüuuuuÙÚÛÜUUUUçÇñÑýÝ',  
            'aaaaaaaaaAAAAAAAAAeeeeeeeeeEEEEEEEEiiiiiiiiIIIIIIIIooooooooOOOOOOOOuuuuuuuuUUUUUUUUcCnNyY') as nome, 
        ST_AsGeoJSON(ST_Transform(ST_SetSRID(geom,32322),4326)) as geojson,
        ST_AsGeoJSON(ST_Centroid(ST_Transform(ST_SetSRID(geom,32322),4326))) as centroid
    from limites_legais.divisa_de_bairros
    order by nome
    ''', conn)

    df.to_csv('data/geojson_curitiba_inicial.csv')
    print(df)

    #df = pd.read_csv('data/geojson_curitiba_inicial.csv')
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

    with open('data/geojson_curitiba.json', 'w') as f:
        json.dump(geojson, f)

if __name__ == '__main__':
    main()