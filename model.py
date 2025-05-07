from tensorflow.keras.models import load_model 

# Load the model with the .hdf5 extension
model = load_model('E:/Git/food_detection/EfficientNetB1.hdf5')

# Save the model with the .h5 extension
model.save('E:/Git/food_detection/EfficientNetB1.h5')
