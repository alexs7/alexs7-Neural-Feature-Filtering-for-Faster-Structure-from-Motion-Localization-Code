import cv2
import os

def save_debug_image(image_gt_path, keypoints_xy, predictions, comparison_data_path, query_image):
    query_image_file = cv2.imread(image_gt_path)
    verif_img = query_image_file.copy()  # need a copy here
    for kp in keypoints_xy:
        kp = kp.astype(int)
        cv2.circle(verif_img, (kp[0], kp[1]), 4, (0, 0, 255), -1)  # red
    for kp in keypoints_xy[predictions == 1]:  # only positive ones
        kp = kp.astype(int)
        cv2.circle(verif_img, (kp[0], kp[1]), 4, (0, 255, 0), -1)  # green

    # Save image to disk
    verif_img_path = os.path.join(comparison_data_path, query_image.split('/')[1])
    cv2.imwrite(verif_img_path, verif_img)