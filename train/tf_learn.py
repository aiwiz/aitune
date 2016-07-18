import tensorflow as tf
import numpy as np
import pdb

# Load datasets.
training_set = tf.contrib.learn.datasets.base.load_csv(filename="spytrain", target_dtype=np.int)
test_set = tf.contrib.learn.datasets.base.load_csv(filename="spytest", target_dtype=np.int)

x_train, x_test, y_train, y_test = training_set.data, test_set.data, training_set.target, test_set.target

# Build 3 layer DNN with 10, 20, 10 units respectively.
classifier = tf.contrib.learn.DNNClassifier(hidden_units=[10, 20, 10], n_classes=3)

# Fit model.
classifier.fit(x=x_train, y=y_train, steps=200)

pdb.set_trace()

# Evaluate accuracy.
accuracy_score_train = classifier.evaluate(x=x_train, y=y_train)["accuracy"]
print('Accuracy on training set: {0:f}'.format(accuracy_score_train))

accuracy_score_test = classifier.evaluate(x=x_test, y=y_test)["accuracy"]
print('Accuracy on test set: {0:f}'.format(accuracy_score_test))

