import os, json, re

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from sklearn import datasets
import numpy as np
import lime
import lime.lime_tabular

app = Flask(__name__)
column_order = joblib.load('models/column_order.joblib') 
model = joblib.load('models/model.joblib') 

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"response": "hello world!"})

def lime_explain(input):
    boston = datasets.load_boston()
    categorical_features = np.argwhere(np.array([len(set(boston.data[:,x])) for x in range(boston.data.shape[1])]) <= 10).flatten()
    explainer = lime.lime_tabular.LimeTabularExplainer(boston.data, feature_names=boston.feature_names, class_names=['price'], categorical_features=categorical_features, verbose=True, mode='regression')
    exp = explainer.explain_instance(np.array(input), model.predict, num_features=5).as_list()

    lime_feature_contributions = {}
    for feature, contribution in exp:
        feature_name = re.findall("[a-zA-Z]+", feature)[0]
        lime_feature_contributions[f'LIME_{feature_name}'] = contribution
    return lime_feature_contributions


@app.route('/predict', methods=['POST'])
def predict():
    request_payload = request.json
    input_features = pd.DataFrame([], columns=column_order)
    input_features = input_features.append(request_payload, ignore_index=True)
    input_features = input_features.fillna(0)

    prediction = model.predict(input_features.values.tolist()).tolist()[0]

    feature_names = column_order.tolist()
    feature_values = input_features.values.tolist()[0]
    lime_feature_contributions = lime_explain(feature_values)

    log_payload = {'prediction': prediction, **dict(zip(feature_names, feature_values)), **lime_feature_contributions}
    print('*****************')
    # TODO some proper logging here
    print(log_payload)
    print('*****************')

    return jsonify({'predicted price (thousands)': prediction})

if __name__ == '__main__':    
    import settings
    if settings.PORT == 5555:
        app.run(port=settings.PORT, host='0.0.0.0', debug=True)
    else:
        app.run()
