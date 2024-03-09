from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
import pickle

class ActiveLevelPredictor():
    def __init__(self):
        self.active_level_classifier = pickle.load(open('./models/active_level_classification_model.pkl', 'rb'))
        self.labels = ['active', 'relaxed', 'sleepy']
        
    def predict(self, data: pd.DataFrame):

        # Perform necessary transformations
        data['Age'] = data['Age'].astype(int)

        oe = OrdinalEncoder(categories=[['F', 'M']])
        data['Gender'] = oe.fit_transform(data[['Gender']])

        # Predict
        predicted_active_level_idx = self.active_level_classifier.predict(data)[0]
        return self.labels[predicted_active_level_idx]