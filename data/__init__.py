from .voc0712 import VOCDetection, VOCAnnotationTransform, VOC_CLASSES, VOC_ROOT
#
# from .coco import COCODetection, COCOAnnotationTransform, COCO_CLASSES, COCO_ROOT, get_label_map
from .config import *
import torch
import cv2
import numpy as np


def collate_fn(batch):
    data, labels = zip(*batch)
    stacked_data = torch.stack(data, dim=0)

    # deal with labels s.t. instead of list of dicts we have list of tensors of size n x 5
    # where n is no. objects in that image

    # at same time remove from batch anything with zero objects
    zipped = [(q, torch.cat((label['boxes'], label['labels'].unsqueeze(1)), 1)) for q, label in enumerate(labels) if len(label['boxes']) > 0]

    indices, stacked_labels = zip(*zipped)
    stacked_data = stacked_data[list(indices)]
    return stacked_data, stacked_labels


def detection_collate(batch):
    """Custom collate fn for dealing with batches of images that have a different
    number of associated object annotations (bounding boxes).

    Arguments:
        batch: (tuple) A tuple of tensor images and lists of annotations

    Return:
        A tuple containing:
            1) (tensor) batch of images stacked on their 0 dim
            2) (list of tensors) annotations for a given image are stacked on
                                 0 dim
    """
    targets = []
    imgs = []
    for sample in batch:
        imgs.append(sample[0])
        targets.append(torch.FloatTensor(sample[1]))
    return torch.stack(imgs, 0), targets


def base_transform(image, size, mean):
    x = cv2.resize(image, (size, size)).astype(np.float32)
    x -= mean
    x = x.astype(np.float32)
    return x


class BaseTransform:
    def __init__(self, size, mean):
        self.size = size
        self.mean = np.array(mean, dtype=np.float32)

    def __call__(self, image, boxes=None, labels=None):
        return base_transform(image, self.size, self.mean), boxes, labels
