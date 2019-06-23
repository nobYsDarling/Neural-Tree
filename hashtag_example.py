import time
from statistics import mean

import tensorflow as tf
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, f1_score
from tensorflow.python import global_variables_initializer
from tensorflow.python.training.adam import AdamOptimizer

from Layers.model import SoftDecisionTree
from lib.helper import get_transformed_hashtag_data, next_batch

if __name__ == '__main__':
    x_train, y_train, x_test, y_test, x_validation, y_validation = get_transformed_hashtag_data()

    n_features = 1001
    n_classes = 101
    batch_size = 32
    val_batch_size = 256

    tree = SoftDecisionTree(max_depth=6, n_features=n_features, n_classes=n_classes, max_leafs=None)
    tree.build_tree()

    # optimizer
    optimizer = AdamOptimizer(learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-08).minimize(
        tree.loss)

    # Saving the model
    # saver = tf.train.Saver()

    # Initialize the variables (i.e. assign their default value)
    init = global_variables_initializer()

    EPOCHS = 1000
    TOTAL_BATCH = 16
    display_step = 100
    with tf.compat.v1.Session() as sess:
        sess.run(init)
        t0 = time.time()

        for epoch in range(EPOCHS):
            avg_cost = 0.
            # Loop over all batches
            acc = 0.0
            val_acc = 0.0
            index_in_epoch = 0
            for i in range(TOTAL_BATCH):
                batch_xs, batch_ys, index_in_epoch = next_batch(
                    x_train,
                    y_train,
                    batch_size,
                    epoch,
                    index_in_epoch
                )

                c = tree.boost(X=batch_xs, y=batch_ys, sess=sess, optimizer=optimizer)

                target = batch_ys
                predictions = tree.predict(X=batch_xs, y=batch_ys, sess=sess)

                acc += mean([
                    mean([1 if p == t else 0 for p, t in zip(pred, targets) if p != 0 or t != 0])
                    for pred, targets
                    in zip(predictions, target)
                ])

                # Compute average loss
                avg_cost += acc / TOTAL_BATCH

            # Display logs per epoch step
            if (epoch + 1) % display_step == 0:
                t1 = time.time()
                print('Trained %d epochs in %f (%fs/epoch)' % (display_step, t1 - t0, (t1 - t0) / display_step))

                batch_val_xs, batch_val_ys, _ = next_batch(
                    x_validation,
                    y_validation,
                    val_batch_size,
                    epoch
                )

                val_target = batch_val_ys
                val_preds = tree.predict(X=batch_val_xs, y=batch_val_ys, sess=sess)
                val_acc = mean([
                    mean([1 if p == t else 0 for p, t in zip(pred, targets) if p != 0 or t != 0])
                    for pred, targets
                    in zip(val_preds, val_target)
                ])

                print("Epoch:", '%04d' % (epoch + 1), "cost=",
                      "{:.9f}".format(avg_cost), "training_accuracy=", "{:.4f}".format(acc),
                      "validation_accuracy=", "{:.4f}".format(val_acc))
                t0 = time.time()
