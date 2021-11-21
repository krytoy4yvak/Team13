from prophet import Prophet
import psycopg2
from psycopg2.extras import execute_batch
from sqlalchemy import create_engine
import pandas as pd


def foo(x):
    if x <30:
        return 1
    elif x >=30 and x < 38:
        return 2
    else:
        return 3


def truncate(df, table, block_id, sensor_id, building_id):
    if df.empty == False:
        conn = psycopg2.connect(host="localhost",
        database="postgres",
        user="junction",
        password="12345")
        df_columns = list(df)
        # create (col1,col2,...)
        columns = ",".join(df_columns)
        # create VALUES('%s', '%s",...) one '%s' per column
        values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
        # create INSERT INTO table (columns) VALUES('%s',...)
        cur = conn.cursor()
        insert_stmt = "INSERT INTO {} ({}) {}".format(table, columns, values)
        drop_table = f"""DELETE from {table} where building_id = {building_id} 
        and block_id = {block_id} and sensor_id = {sensor_id} """
        #cur = conn.cursor()
        cur.execute(drop_table)
        execute_batch(cur, insert_stmt, df.values)
        conn.commit

        cur.close()
        conn.close()


def predict(building_id, block_id,sensor_id, period=30 * 12):
    conn = create_engine('postgresql+psycopg2://junction:12345@localhost/postgres')
    data = pd.read_sql_query(f"""
    Select timestamp, data->>'Consumption' as consumption, data->>'Power_Consumption' as power_consumption, 
    data->>'flowtime' as flowtime
    from public.sensors_data
    where building_id = {building_id} and block_id = {block_id}
    """, con=conn)

    #     print(data)
    col = ['consumption']
    data[col] = data[col].astype(float)
    data['date'] = data['timestamp'].dt.date.astype('datetime64[ns]')


    hours = pd.DataFrame(pd.date_range(data.date.min(), data.date.max(), freq='d'), columns=['date'])
    data = hours.merge(data, how='left', on='date')
    data = data.fillna(0)


    data_hot = data[['date', 'consumption']]
    data_hot.columns = ['ds', 'y']

    model1 = Prophet()
    model1.fit(data_hot)

    future_hot = model1.make_future_dataframe(periods=period, freq='D')
    forecast_hot = model1.predict(future_hot)
    forecast_hot = forecast_hot[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast_hot['yhat_lower'] = forecast_hot['yhat_lower'].apply(lambda x: 0 if x < 0 else x)
    forecast_hot.columns = ['date', 'water_neutral', 'water_lower', 'water_upper']

    forecast_hot['building_id'] = building_id
    forecast_hot['block_id'] = block_id
    forecast_hot['sensor_id'] = sensor_id
    truncate(forecast_hot, 'public.water_forecast_2', block_id, sensor_id, building_id)



