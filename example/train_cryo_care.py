from keras.utils import Sequence
import numpy as np
from csbdeep.models import CARE
from csbdeep.utils import _raise, axes_check_and_normalize, axes_dict
import warnings


def augment(x, y):
    rot_k = np.random.randint(0, 4, x.shape[0])

    X = x.copy()
    Y = y.copy()

    for i in range(X.shape[0]):
        if np.random.rand() < 0.5:
            X[i] = np.rot90(x[i], k=rot_k[i], axes=(0, 2))
            Y[i] = np.rot90(y[i], k=rot_k[i], axes=(0, 2))
        else:
            X[i] = np.rot90(y[i], k=rot_k[i], axes=(0, 2))
            Y[i] = np.rot90(x[i], k=rot_k[i], axes=(0, 2))

    return X, Y


class CryoDataWrapper(Sequence):

    def __init__(self, X, Y, batch_size):
        self.X, self.Y = X, Y
        self.batch_size = batch_size
        self.perm = np.random.permutation(len(self.X))

    def __len__(self):
        return int(np.ceil(len(self.X) / float(self.batch_size)))

    def on_epoch_end(self):
        self.perm = np.random.permutation(len(self.X))

    def __getitem__(self, i):
        idx = slice(i*self.batch_size,(i+1)*self.batch_size)
        idx = self.perm[idx]

        return self.__augment__(self.X[idx], self.Y[idx])

    def __augment__(self, x, y):
        return augment(x, y)
    
    
class CryoCARE(CARE):

    def train(self, X, Y, validation_data, epochs=None, steps_per_epoch=None):
        """Train the neural network with the given data.
        Parameters
        ----------
        X : :class:`numpy.ndarray`
            Array of source images.
        Y : :class:`numpy.ndarray`
            Array of target images.
        validation_data : tuple(:class:`numpy.ndarray`, :class:`numpy.ndarray`)
            Tuple of arrays for source and target validation images.
        epochs : int
            Optional argument to use instead of the value from ``config``.
        steps_per_epoch : int
            Optional argument to use instead of the value from ``config``.
        Returns
        -------
        ``History`` object
            See `Keras training history <https://keras.io/models/model/#fit>`_.
        """

        ((isinstance(validation_data, (list, tuple)) and len(validation_data) == 2)
         or _raise(ValueError('validation_data must be a pair of numpy arrays')))

        n_train, n_val = len(X), len(validation_data[0])
        frac_val = (1.0 * n_val) / (n_train + n_val)
        frac_warn = 0.05
        if frac_val < frac_warn:
            warnings.warn("small number of validation images (only %.1f%% of all images)" % (100 * frac_val))
        axes = axes_check_and_normalize('S' + self.config.axes, X.ndim)
        ax = axes_dict(axes)

        for a, div_by in zip(axes, self._axes_div_by(axes)):
            n = X.shape[ax[a]]
            if n % div_by != 0:
                raise ValueError(
                    "training images must be evenly divisible by %d along axis %s"
                    " (which has incompatible size %d)" % (div_by, a, n)
                )

        if epochs is None:
            epochs = self.config.train_epochs
        if steps_per_epoch is None:
            steps_per_epoch = self.config.train_steps_per_epoch

        if not self._model_prepared:
            self.prepare_for_training()

        training_data = CryoDataWrapper(X, Y, self.config.train_batch_size)

        history = self.keras_model.fit_generator(generator=training_data, validation_data=validation_data,
                                                 epochs=epochs, steps_per_epoch=steps_per_epoch,
                                                 callbacks=self.callbacks, verbose=1)

        if self.basedir is not None:
            self.keras_model.save_weights(str(self.logdir / 'weights_last.h5'))

            if self.config.train_checkpoint is not None:
                print()
                self._find_and_load_weights(self.config.train_checkpoint)
                try:
                    # remove temporary weights
                    (self.logdir / 'weights_now.h5').unlink()
                except FileNotFoundError:
                    pass


        return history
