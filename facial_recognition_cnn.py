# -*- coding: utf-8 -*-
"""BVC_Facial_Recognition_CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QCKJH68qS2uPIZ4VgpQ9q9H0r9jCrDsQ
"""

#import required libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow import keras
import seaborn as sn
from sklearn.metrics import confusion_matrix
from tensorflow.keras import layers
import warnings
warnings.filterwarnings('ignore')

from google.colab import drive
drive.mount("/content/gdrive")

#Read the csv file 
data = pd.read_csv('/content/gdrive/My Drive/fer2013.csv')
data.shape

data.head()

#this dictionary em will be used to map different emotions
em = {0:'Angry', 1:'Disgust', 2:'Fear', 3:'Happy', 4:'Sad', 5:'Surprise', 6:'Neutral'}
#Store the different emotions in a list also
target_names = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

data.Usage.value_counts()

#To see how many samples of each emotion are present

newdf = data.groupby('emotion').size()
newdf = pd.DataFrame(newdf)
newdf.insert(0, "Emotion type", target_names, True)
newdf.columns = [ 'Emotion', 'No of samples']
newdf

# newdf.drop('emotion', inplace=True, axis = 1)

#Separate the training, validation and test data sets
data_train = data[data['Usage'] == 'Training'].copy()
data_val = data[data['Usage'] == 'PublicTest'].copy()
data_test = data[data['Usage'] == 'PrivateTest'].copy()

data_train.info()

#initilize parameters
num_classes = 7 
width, height = 48, 48
num_epochs = 30
batch_size = 32
num_features = 64
input_shape = (width, height, 1)

#this function converts the pixels into a 2D array of size 48x48 and does one-hot encoding for the emotions
from tensorflow.keras.utils import to_categorical
def CRNO(df, dataName):
    df['pixels'] = df['pixels'].apply(lambda pixel_sequence: [int(pixel) for pixel in pixel_sequence.split()])
    data_X = np.array(df['pixels'].tolist(), dtype='float32').reshape(-1,width, height,1)/255.0  
    data_Y = to_categorical(df['emotion'], num_classes)  
    print(dataName, "_X shape: {}, ", dataName, "_Y shape: {}".format(data_X.shape, data_Y.shape)) 
    return data_X, data_Y

    
train_X, train_Y = CRNO(data_train, "train") #training data
val_X, val_Y     = CRNO(data_val, "val") #validation data
test_X, test_Y   = CRNO(data_test, "test") #test data

#Let us see some of the images and their target emotions

plt.figure(figsize=(16, 10))

plt.gray()
flag = 0
i= 1
cnt = 0
for i in range(1,8):
        plt.subplot(2, 4, i)
        plt.imshow(train_X[i].reshape(width, height))
        plt.title(em[data_train.emotion[i]])
        plt.axis('off')    
       

plt.show()

from keras.layers.convolutional import Conv2D, MaxPooling2D
from tensorflow.keras.layers import BatchNormalization
from keras.layers import Dense, Dropout, Activation, Flatten
model = keras.Sequential()

#Add the different layers to the model

# model = keras.Sequential(
#     [
#         keras.Input(shape=input_shape),
#         #module 1
#         layers.Conv2D(num_features, kernel_size=(3, 3), activation="relu"),
        
#         layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
        
#         layers.Conv2D(2*num_features, kernel_size=(3, 3), activation="relu"),
#         layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
       
#         layers.Conv2D(2*num_features, kernel_size=(3, 3), activation="relu"),
#         layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
        
#         layers.Conv2D(8*num_features, kernel_size=(3, 3), activation="relu"),
#         layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
#         layers.Flatten(),
#         layers.Dense(num_classes, activation="softmax"),
#     ]
# )
# model.summary()

#module 1
model.add(Conv2D(num_features, kernel_size=(3, 3), input_shape=(width, height, 1), data_format='channels_last'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(num_features, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

#module 2
model.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

#module 3
model.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))


#module 4
model.add(Conv2D(num_features*8, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(num_features*8, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(num_features*8, kernel_size=(3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

#flatten
model.add(Flatten())

#dense 1
model.add(Dense(64*num_features))
model.add(BatchNormalization())
model.add(Activation('relu'))

#dense 2
model.add(Dense(64*num_features))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Dropout(0.3))

#output layer
model.add(Dense(num_classes, activation='softmax'))

#train the model
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(train_X, train_Y, batch_size=batch_size, epochs=num_epochs, validation_data=(val_X, val_Y))
model.summary()

#To check our model's score on validation and test data
score = model.evaluate(val_X, val_Y, verbose = 0)
print("Val loss:", score[0])
print("Val accuracy: ", score[1])

score = model.evaluate(test_X, test_Y, verbose=0)
print("Test loss:", score[0])
print("Test accuracy:", score[1])

from keras.callbacks import History 
history = History()

predict_prob = model.predict(test_X)
pred = np.argmax(predict_prob,axis=1)
actual = np.argmax(test_Y,axis=1)

#display confusion matrix
cm = confusion_matrix(data_test.emotion, pred)
df_cm = pd.DataFrame(cm, (emotion for emotion in target_names), (emotion for emotion in target_names))
plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True, fmt='g')
plt.xlabel('Predicted')
plt.ylabel('Truth')
plt.show()

#his code snippet is for displaying the classification report
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
print(classification_report(data_test['emotion'], pred, target_names=target_names, digits=2))

# Check Accuracy of each class 

#Normalize the entries
cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

#The diagonal entries are the accuracies of each class
cm.diagonal()
d ={'Emotion': target_names, 'Accuracy': cm.diagonal()}
df = pd.DataFrame(d)
df