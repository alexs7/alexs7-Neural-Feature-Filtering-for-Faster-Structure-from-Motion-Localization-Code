# run this to get the avg of the 3D desc of a point same order as in points3D
# be careful that you can get the base model's avg descs or the live's model descs - depends on the points images ids

# the idea here is that a point is seen by the base model images and live model images
# obviously the live model images number > base model images number for a point

import numpy as np
from database import COLMAPDatabase
from parameters import Parameters
from point3D_loader import read_points3d_default, index_dict
from query_image import read_images_binary, get_images_ids, get_images_names_from_sessions_numbers

def get_desc_avg(points3D, db):
    points_mean_descs = np.empty([0, 128])

    for k,v in points3D.items():
        point_id = v.id
        points3D_descs = np.empty([0, 128])
        points_image_ids = points3D[point_id].image_ids #COLMAP adds the image twice some times.
        # Loop through the points' image ids and check if it is seen by any image_ids
        # If it is seen then get the desc for each id.
        for k in range(len(points_image_ids)):
            id = points_image_ids[k]
            data = db.execute("SELECT data FROM descriptors WHERE image_id = " + "'" + str(id) + "'")
            data = COLMAPDatabase.blob_to_array(data.fetchone()[0], np.uint8)
            descs_rows = int(np.shape(data)[0] / 128)
            descs = data.reshape([descs_rows, 128]) #descs for the whole image
            keypoint_index = points3D[point_id].point2D_idxs[k]
            desc = descs[keypoint_index] #keypoints and descs are ordered the same (so I use the point2D_idxs to index descs )
            desc = desc.reshape(1, 128) #this is the desc of keypoint with index, keypoint_index, from image with id, id.
            desc = desc / desc.sum()
            points3D_descs = np.r_[points3D_descs, desc]

        # adding and calulating the mean here!
        points_mean_descs = np.r_[points_mean_descs, points3D_descs.mean(axis=0).reshape(1,128)]
    return points_mean_descs

# colmap_features_no can be "2k", "1k", "0.5k", "0.25k"
# exponential_decay can be any of 0.1 to 0.9
features_no = "1k"
exponential_decay_value = 0.5

print("-- Averaging features_no " + features_no + " --")

db_live = COLMAPDatabase.connect(Parameters.live_db_path)
db_base = COLMAPDatabase.connect(Parameters.base_db_path)

base_model_images = read_images_binary(Parameters.base_model_images_path)
base_model_points3D = read_points3d_default(Parameters.base_model_points3D_path)

live_model_images = read_images_binary(Parameters.live_model_images_path)
live_model_points3D = read_points3d_default(Parameters.live_model_points3D_path)

# You will notice that I am using live_model_points3D in both cases, fetching avg features for the base images and the live images.
# This is because the live_model_points3D points' images_ids hold also ids of the live and base model images, since the live model is just the
# base model with extra images localised in it. You can use the base model for the base images but you need to make sure that the base model is exactly the
# same as the live model, before you do. TODO: Maybe change to base to get it done with ?

# 2 cases base and live images points3D descs
avgs_base = get_desc_avg(base_model_points3D, db_base)
np.save(Parameters.avg_descs_base_path, avgs_base)

avgs_live = get_desc_avg(live_model_points3D, db_live)
np.save(Parameters.avg_descs_live_path, avgs_live)
