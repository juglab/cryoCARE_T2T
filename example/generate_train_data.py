import mrcfile
import numpy as np


def compute_mean_std(data):
    """
    Compute mean and standard deviation of a given image file.
    
    Parameters
    ----------
    data : array(float)
        The data.
        
    Returns
    -------
    float
        mean
    float
        standard deviation
    """
    mean, std = np.mean(data), np.std(data)
        
    return mean, std


def sample_coordinates(mask, num_train_vols, num_val_vols, vol_dims=(96, 96, 96)):
    """
    Sample random coordinates for train and validation volumes. The train and validation 
    volumes will not overlap. The volumes are only sampled from foreground regions in the mask.
    
    Parameters
    ----------
    mask : array(int)
        Binary image indicating foreground/background regions. Volumes will only be sampled from 
        foreground regions.
    num_train_vols : int
        Number of train-volume coordinates.
    num_val_vols : int
        Number of validation-volume coordinates.
    vol_dims : tuple(int, int, int)
        Dimensionality of the extracted volumes. Default: ``(96, 96, 96)``
        
    Returns
    -------
    list(tuple(slice, slice, slice))
        Training volume coordinates.
     list(tuple(slice, slice, slice))
        Validation volume coordinates.
    """
    cent = (np.array(vol_dims) / 2).astype(np.int32)
    mask[:cent[0]] = 0
    mask[-cent[0]:] = 0
    mask[:, :cent[1]] = 0
    mask[:, -cent[1]:] = 0
    mask[:, :, :cent[2]] = 0
    mask[:, :, -cent[2]:] = 0
    
    tv_span = np.round(np.array(vol_dims) / 2).astype(np.int32)
    span = np.round(np.array(mask.shape) * 0.1 / 2 ).astype(np.int32)
    val_sampling_mask = mask.copy()
    val_sampling_mask[:, :span[1]] = 0
    val_sampling_mask[:, -span[1]:] = 0
    val_sampling_mask[:, :, :span[2]] = 0
    val_sampling_mask[:, :, -span[2]:] = 0
    foreground_pos = np.where(val_sampling_mask)
    sample_inds = np.random.choice(len(foreground_pos[0]), 2, replace=False)

    val_sampling_mask = np.zeros(mask.shape, dtype=np.int8)
    val_sampling_inds = [fg[sample_inds] for fg in foreground_pos]
    for z, y, x in zip(*val_sampling_inds):
        val_sampling_mask[z - span[0]:z + span[0],
        y - span[1]:y + span[1],
        x - span[2]:x + span[2]] = mask[z - span[0]:z + span[0],
                                        y - span[1]:y + span[1],
                                        x - span[2]:x + span[2]].copy()

        mask[max(0, z - span[0] - tv_span[0]):min(mask.shape[0], z + span[0] + tv_span[0]),
        max(0, y - span[1] - tv_span[1]):min(mask.shape[1], y + span[1] + tv_span[1]),
        max(0, x - span[2] - tv_span[2]):min(mask.shape[2], x + span[2] + tv_span[2])] = 0

    foreground_pos = np.where(val_sampling_mask)
    sample_inds = np.random.choice(len(foreground_pos[0]), num_val_vols, replace=num_val_vols<len(foreground_pos[0]))
    val_sampling_inds = [fg[sample_inds] for fg in foreground_pos]
    val_coords = []
    for z, y, x in zip(*val_sampling_inds):
        val_coords.append(tuple([slice(z-tv_span[0], z+tv_span[0]),
                                 slice(y-tv_span[1], y+tv_span[1]),
                                 slice(x-tv_span[2], x+tv_span[2])]))

    foreground_pos = np.where(mask)
    sample_inds = np.random.choice(len(foreground_pos[0]), num_train_vols, replace=num_train_vols < len(foreground_pos[0]))
    train_sampling_inds = [fg[sample_inds] for fg in foreground_pos]
    train_coords = []
    for z, y, x in zip(*train_sampling_inds):
        train_coords.append(tuple([slice(z - tv_span[0], z + tv_span[0]),
                                 slice(y - tv_span[1], y + tv_span[1]),
                                 slice(x - tv_span[2], x + tv_span[2])]))

    return train_coords, val_coords


def normalize(img, mean, std):
    """
    Normalize image with mean and standard deviation.
    
    Parameters
    ----------
    img : array(float)
        The image to normalize
    mean : float
        The mean used for normalization.
    std : float
        The standard deviation used for normalization.
        
    Returns
    -------
    array(float)
        The normalized image.
    """
    return (img - mean) / std


def denormalize(img, mean, std):
    """
    Denormalize the image with mean and standard deviation. This inverts
    the normalization.
    
    Parameters
    ----------
    img : array(float)
        The image to denormalize.
    mean : float
        The mean which was used for normalization.
    std : float
        The standard deviation which was used for normalization.
    """
    return (img * std) + mean


def extract_volumes(even, odd, train_coords, val_coords, mean, std):
    """
    Extract train and validation volumes and normalize them.
    
    Parameters
    ----------
    even : array(float)
        Even tomogram.
    odd : array(float)
        Odd tomogram.
    train_coords : list(tuple(slice, slice, slice))
        The slices of the train-volumes.
    val_coords : list(tuple(slice, slice, slice))
        The slices of the validation-volumes.
    mean : float
        Mean used for normalization.
    std : float
        Standard deviation used for normalization.
        
    Returns
    -------
    list(array(float))
        Train data X (normalized)
    list(array(float))
        Train data Y (normalized)
    list(array(float))
        Validation data X_val (normalized)
    list(array(float))
        Validation data Y_val (normalized)
    """
    z, y, x = train_coords[0][0], train_coords[0][1], train_coords[0][2]
    train_vol_dims = (z.stop - z.start, y.stop - y.start, x.stop - x.start)
    z, y, x = val_coords[0][0], val_coords[0][1], val_coords[0][2]
    val_vol_dims = (z.stop - z.start, y.stop - y.start, x.stop - x.start)
    
    X = np.zeros((len(train_coords), *train_vol_dims), dtype=np.float32)
    Y = np.zeros((len(train_coords), *train_vol_dims), dtype=np.float32)
    X_val = np.zeros((len(val_coords), *val_vol_dims), dtype=np.float32)
    Y_val = np.zeros((len(val_coords), *val_vol_dims), dtype=np.float32)

    img_x = even
    img_x = normalize(img_x, mean, std)
    img_y = odd
    img_y = normalize(img_y, mean, std)

    for i, pos in enumerate(train_coords):
        X[i] = img_x[pos]
        Y[i] = img_y[pos]

    for i, pos in enumerate(val_coords):
        X_val[i] = img_x[pos]
        Y_val[i] = img_y[pos]


    X = X[..., np.newaxis]
    Y = Y[..., np.newaxis]
    X_val = X_val[..., np.newaxis]
    Y_val = Y_val[..., np.newaxis]

    return X, Y, X_val, Y_val
