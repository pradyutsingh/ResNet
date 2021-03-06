import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

import tensorflow.keras
from tensorflow.keras.layers import Conv2D , Dropout , MaxPool2D, AvgPool2D, Add, Dense
from tensorflow.keras.preprocessing.image import load_img , img_to_array

import warnings
warnings.warn("ignore")

import os
os.listdir('intel-image-classification')


def convert(path,y):
    array=[]
    imgX = []
    for img_path in os.listdir(path):
        img = load_img(path + img_path, target_size=(150,150))
        img = img_to_array(img)
        img = img/255.
        array.append(img)
        imgX.append(y)
    return np.array(array), np.array(imgX)

X_train_building , Y_train_building = convert("intel-image-classification/seg_train/seg_train/buildings/",0)
X_train_forest , Y_train_forest = convert("intel-image-classification/seg_train/seg_train/forest/",1)
X_train_glacier , Y_train_glacier = convert("intel-image-classification/seg_train/seg_train/glacier/",2)
X_train_mountain , Y_train_mountain  = convert("intel-image-classification/seg_train/seg_train/mountain/",3)
X_train_sea, Y_train_sea  = convert("intel-image-classification/seg_train/seg_train/sea/",4)
X_train_street , Y_train_street  = convert("intel-image-classification/seg_train/seg_train/street/",5)

print('train building ', X_train_building.shape, Y_train_building.shape) 
print('train forest', X_train_forest.shape ,Y_train_forest.shape)
print('train glacier', X_train_glacier.shape,Y_train_glacier.shape)
print('train mountain', X_train_mountain.shape, Y_train_mountain.shape)
print('train sea',     X_train_sea.shape, Y_train_sea.shape)
print('train street', X_train_street.shape ,Y_train_street.shape)

X_train= np.concatenate((X_train_building,X_train_forest, X_train_glacier,X_train_mountain, X_train_sea,X_train_street),axis=0)
Y_train= np.concatenate((Y_train_building,Y_train_forest,Y_train_glacier,Y_train_mountain, Y_train_sea,Y_train_street),axis=0)

X_test_building, Y_test_building  = convert("intel-image-classification/seg_test/seg_test/buildings/",0)
X_test_forest,Y_test_forest  = convert("intel-image-classification/seg_test/seg_test/forest/",1)
X_test_glacier,Y_test_glacier  = convert("intel-image-classification/seg_test/seg_test/glacier/",2)
X_test_mountain,Y_test_mountain  = convert("intel-image-classification/seg_test/seg_test/mountain/",3)
X_test_sea,Y_test_sea  = convert("intel-image-classification/seg_test/seg_test/sea/",4)
X_test_street,Y_test_street  = convert("intel-image-classification/seg_test/seg_test/street/",5)

print('test building  ', X_test_building.shape, Y_test_building.shape) 
print('test forest', X_test_forest.shape ,Y_test_forest.shape)
print('test glacier', X_test_glacier.shape,Y_test_glacier.shape)
print('test mountain', X_test_mountain.shape, Y_test_mountain.shape)
print('test sea',     X_test_sea.shape, Y_test_sea.shape)
print('test street', X_test_street.shape ,Y_test_street.shape)

X_test= np.concatenate((X_test_building,X_test_forest, X_test_glacier,X_test_mountain, X_test_sea,X_test_street),axis=0)
Y_test= np.concatenate((Y_test_building,Y_test_forest, Y_test_glacier,Y_test_mountain, Y_test_sea,Y_test_street),axis=0)

X_train.shape,X_test.shape,Y_train.shape,Y_test.shape

from tensorflow.keras.utils import to_categorical

Y_train = to_categorical(Y_train)
Y_test = to_categorical(Y_test)
Y_train.shape , Y_test.shape
Y_test[1]

def identity_block(X, f, filters, stage, block):
    # defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    # Retrieve Filters
    F1, F2, F3 = filters

    # Save the input value. We'll need this later to add back to the main path. 
    X_shortcut = X

    # First component of main path
    X = Conv2D(filters = F1, kernel_size = (1, 1), strides = (1,1), padding = 'valid', name = conv_name_base + '2a', kernel_initializer = glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis = 3, name = bn_name_base + '2a')(X)
    X = Activation('relu')(X)

    # Second component of main path
    X = Conv2D(filters = F2, kernel_size = (f, f), strides = (1,1), padding = 'same', name = conv_name_base + '2b', kernel_initializer = glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis = 3, name = bn_name_base + '2b')(X)
    X = Activation('relu')(X)

    # Third component of main path
    X = Conv2D(filters = F3, kernel_size = (1, 1), strides = (1,1), padding = 'valid', name = conv_name_base + '2c', kernel_initializer = glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis = 3, name = bn_name_base + '2c')(X)

    # Final step: Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X, X_shortcut])
    X = Activation('relu')(X)

    return X

def convolutional_block(X, f, filters, stage, block, s = 2):
    # defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'
    
    # Retrieve Filters
    F1, F2, F3 = filters
    
    # Save the input value
    X_shortcut = X


    ##### MAIN PATH #####
    # First component of main path 
    X = Conv2D(F1, (1, 1), strides = (s,s), name = conv_name_base + '2a', kernel_initializer = glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis = 3, name = bn_name_base + '2a')(X)
    X = Activation('relu')(X)

    # Second component of main path
    X = Conv2D(filters=F2, kernel_size=(f, f), strides=(1, 1), padding='same', name=conv_name_base + '2b', kernel_initializer=glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2b')(X)
    X = Activation('relu')(X)

    # Third component of main path
    X = Conv2D(filters=F3, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2c', kernel_initializer=glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2c')(X)

    
    ##### SHORTCUT PATH ####
    X_shortcut = Conv2D(F3, (1, 1), strides = (s,s), name = conv_name_base + '1', kernel_initializer = glorot_uniform(seed=0))(X_shortcut)
    X_shortcut = BatchNormalization(axis = 3, name = bn_name_base + '1')(X_shortcut)

    # Final step: Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X, X_shortcut])
    X = Activation('relu')(X)
    
    return X
    

def ResNet50(input_shape = (150, 150, 3), classes = 6):   
    # Define the input as a tensor with shape input_shape
    X_input = input(input_shape)
    # Zero-Padding
    X = ZeroPadding2D((3, 3))(X_input)
    
    # Stage 1
    X = Conv2D(64, (7, 7), strides = (2, 2), name = 'conv1', kernel_initializer = glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis = 3, name = 'bn_conv1')(X)
    X = Activation('relu')(X)
    X = MaxPooling2D((3, 3), strides=(2, 2))(X)

    # Stage 2
    X = convolutional_block(X, f = 3, filters = [64, 64, 256], stage = 2, block='a', s = 1)
    X = identity_block(X, 3, [64, 64, 256], stage=2, block='b')
    X = identity_block(X, 3, [64, 64, 256], stage=2, block='c')

    # Stage 3
    X = convolutional_block(X, f = 3, filters = [128, 128, 512], stage = 3, block='a', s = 2)
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='b')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='c')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='d')

    # Stage 4
    X = convolutional_block(X, f = 3, filters = [256, 256, 1024], stage = 4, block='a', s = 2)
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='b')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='c')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='d')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='e')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='f')

    # Stage 5
    X = convolutional_block(X, f = 3, filters = [512, 512, 2048], stage = 5, block='a', s = 2)
    X = identity_block(X, 3, [512, 512, 2048], stage=5, block='b')
    X = identity_block(X, 3, [512, 512, 2048], stage=5, block='c')

    # AVGPOOL.
    X = AveragePooling2D((2, 2), name='avg_pool')(X)

    # output layer
    X = Flatten()(X)
    X = Dropout(0.3)(X)
    X = Dense(classes, activation='softmax', name='fc' + str(classes), kernel_initializer = glorot_uniform(seed=0))(X)
    
    # Create model
    model = Model(inputs = X_input, outputs = X, name='ResNet50')

    return model

model = ResNet50(input_shape = (150, 150, 3), classes = 6)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

Xmod=model.fit(X_train, y_train, epochs = 50, batch_size = 64,validation_data=(X_test, y_test), shuffle=True)

model.evaluate(X_test, y_test)

fig = plt.subplots(figsize=(12,10))
plt.plot(Xmod.Xmod['loss'], color='b', label="Training loss")
plt.plot(Xmod.Xmod['val_loss'], color='r', label="validation loss")
plt.legend(loc='best', shadow=True)