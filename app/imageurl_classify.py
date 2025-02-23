import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os
import requests
from io import BytesIO

class ImageClassifier:
    def __init__(self):
        self.model_path = r'classifier1.keras'
        self.confidence_threshold = 0.5
        self.model = self._load_model()
        self.num_classes = self.model.output_shape[-1]
        self.class_labels = self._get_class_labels()
        
    def _load_model(self):
        print("Current working directory:", os.getcwd())
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        
        return tf.keras.models.load_model(
            self.model_path,
            custom_objects={
                'MobileNet': tf.keras.applications.MobileNet,
                'GlobalAveragePooling2D': tf.keras.layers.GlobalAveragePooling2D
            }
        )
        
    def _get_class_labels(self):
        if self.num_classes == 13:
            return [
                'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 
                'Effusion', 'Emphysema', 'Fibrosis', 'Infiltration', 
                'Mass', 'Nodule', 'Pleural_Thickening', 'Pneumonia', 
                'Pneumothorax'
            ]
        else:
            return [f'Class_{i}' for i in range(self.num_classes)]
        
    def _preprocess_image(self, img_array):
        return img_array.astype('float32') / 255.0
        
    def _load_image_from_url(self, image_url):
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download image from {image_url}")
        
        return load_img(BytesIO(response.content), target_size=(128, 128), color_mode='grayscale')
        
    def classify(self, image_source, is_url=True):
        try:
            if is_url:
                img = self._load_image_from_url(image_source)
            else:
                img = load_img(image_source, target_size=(128, 128), color_mode='grayscale')
            
            x = img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = self._preprocess_image(x)

            predictions = self.model.predict(x, verbose=0)[0]
            
            labels = [self.class_labels[i] for i in range(self.num_classes) if predictions[i] >= self.confidence_threshold]
            # get a list of confidence values crossing the threshold for each label
            confidences = [predictions[i] for i in range(self.num_classes) if predictions[i] >= self.confidence_threshold]
            
            if not labels:
                labels.append(self.class_labels[np.argmax(predictions)])
                confidences.append(predictions[np.argmax(predictions)])
            
            return {
                "labels": ", ".join(labels),
                "confidence_scores": ", ".join(map(str, confidences))
            }
        
        except Exception as e:
            print(f"Error during classification: {str(e)}")
            return ""

    

# Example usage
if __name__ == "__main__":
    classifier = ImageClassifier()
    
    image_url = "https://firebasestorage.googleapis.com/v0/b/xspand-db058.firebasestorage.app/o/00000506_017.png?alt=media&token=99d68440-cfb4-42dc-986e-a3c810c84af8"
    result = classifier.classify(image_url)
    print("Classified Labels:", result)
