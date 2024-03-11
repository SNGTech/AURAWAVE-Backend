from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
import pickle

class EmotionPredictor():
    def __init__(self):
        self.emotion_classifier = pickle.load(open('./models/active_level_classification_model.pkl', 'rb'))
        self.labels = ['happy', 'relaxed', 'sad']
        
    def predict(self, data: pd.DataFrame):

        # Perform necessary transformations
        data['Age'] = data['Age'].astype(int)

        oe = OrdinalEncoder(categories=[['F', 'M']])
        data['Gender'] = oe.fit_transform(data[['Gender']])

        # Predict
        predicted_emotion_idx = self.emotion_classifier.predict(data)[0]
        return self.labels[predicted_emotion_idx]
