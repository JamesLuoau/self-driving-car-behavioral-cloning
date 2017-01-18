import numpy as np
import cv2
import scipy
from data_load import FeedingData


def center_image_generator(drive_record):
    return drive_record.center_image(), drive_record.steering_angle


def left_image_generator(drive_record):
    return drive_record.left_image(), drive_record.steering_angle + 0.2


def right_image_generator(drive_record):
    return drive_record.right_image(), drive_record.steering_angle - 0.2


def center_left_right_image_generator(drive_record):
    generator = random_generators(center_image_generator, left_image_generator, right_image_generator)
    return generator(drive_record)


def random_generators(*generators):
    def _generator(feeding_data):
        index = np.random.randint(0, len(generators))
        return generators[index](feeding_data)

    return _generator


def pipe_line_generators(*generators):
    """
    pipe line of generators, generator will run one by one
    :param generators:
    :return:
    """
    def _generator(feeding_data):
        intermediary_feeding_data = feeding_data
        for generator in generators:
            image, angle = generator(intermediary_feeding_data)
            intermediary_feeding_data = FeedingData(image, angle)
        return intermediary_feeding_data.image(), intermediary_feeding_data.steering_angle

    return _generator


def _shift_image(image, steer, left_right_shift_range, top_bottom_shift_range):
    tr_x = round(left_right_shift_range * np.random.uniform(-0.5, 0.5))
    steer_ang = steer + tr_x * .002
    tr_y = round(top_bottom_shift_range * np.random.uniform(-0.5, 0.5))
    image_tr = scipy.ndimage.interpolation.shift(image, (tr_y, tr_x, 0))
    return image_tr, steer_ang, tr_x


def trans_image(image, steer, trans_range):
    # Translation
    tr_x = trans_range * np.random.uniform() - trans_range / 2
    steer_ang = steer + tr_x / trans_range * 2 * .2
    tr_y = 10 * np.random.uniform() - 10 / 2
    # tr_y = 0
    Trans_M = np.float32([[1, 0, tr_x], [0, 1, tr_y]])
    image_tr = cv2.warpAffine(image, Trans_M, (3, 1))

    return image_tr, steer_ang, tr_x