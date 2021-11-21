from sklearn.ensemble import IsolationForest
import pandas as pd
from sqlalchemy import create_engine
from forecast import truncate


def anomaly_find(building_id, block_id, sensor_id):
    i_for = IsolationForest(n_estimators = 100, random_state = 42, bootstrap=True)
    conn = create_engine('postgresql+psycopg2://junction:12345@localhost/postgres')
    data = pd.read_sql_query(f"""
        Select timestamp, data->>'Power_Consumption' as power_consumption, data->>'FlowTime' as flowtime,
         building_id, block_id, sensor_id
        from public.sensors_data
        where building_id = {building_id} and block_id = {block_id} and sensor_id = {sensor_id}
        """, con=conn)
    col = ['power_consumption', 'flowtime']
    data[col] = data[col].astype(float)
    data['cost'] = (data['power_consumption']) * (data['flowtime'] / 3600)
    i_for.fit(data[['cost']])
    pred_train = i_for.predict(data[['cost']])
    data['anomaly'] = pred_train
    data['building_id'] = building_id
    data['block_id'] = block_id
    data['sensor_id'] = sensor_id
    truncate(data[data['anomaly'] == -1][['timestamp',
                                          'building_id','block_id','sensor_id']].reset_index(drop=True), 'public.anomaly', building_id, block_id, sensor_id)