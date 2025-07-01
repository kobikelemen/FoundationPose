from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np
import io, zipfile, tempfile, logging, base64, os


from estimater import *
from datareader import *
import argparse



app = FastAPI()
logging.basicConfig(level=logging.INFO)


def _compute_pose(data_dir : str):
#   parser = argparse.ArgumentParser()
  code_dir = os.path.dirname(os.path.realpath(__file__))
#   parser.add_argument('--mesh_file', type=str, default=f'{code_dir}/demo_data/mustard0/mesh/textured_simple.obj')
#   parser.add_argument('--test_scene_dir', type=str, default=f'{code_dir}/demo_data/mustard0')
#   parser.add_argument('--est_refine_iter', type=int, default=5)
#   parser.add_argument('--track_refine_iter', type=int, default=2)
#   parser.add_argument('--debug', type=int, default=1)
#   parser.add_argument('--debug_dir', type=str, default=f'{code_dir}/debug')

  mesh_file = f"{code_dir}/mesh/textured_simple.obj"
  est_refine_iter = 5
  track_refine_iter = 2
  debug = 2
  debug_dir = "debug_dir"
#   args = parser.parse_args()

  set_logging_format()
  set_seed(0)

  mesh = trimesh.load(mesh_file)

  os.system(f'rm -rf {debug_dir}/* && mkdir -p {debug_dir}/track_vis {debug_dir}/ob_in_cam')

  to_origin, extents = trimesh.bounds.oriented_bounds(mesh)
  bbox = np.stack([-extents/2, extents/2], axis=0).reshape(2,3)

  scorer = ScorePredictor()
  refiner = PoseRefinePredictor()
  glctx = dr.RasterizeCudaContext()
  est = FoundationPose(model_pts=mesh.vertices, model_normals=mesh.vertex_normals, mesh=mesh, scorer=scorer, refiner=refiner, debug_dir=debug_dir, debug=debug, glctx=glctx)
  logging.info("estimator initialization done")

  reader = YcbineoatReader(video_dir=data_dir, shorter_side=None, zfar=np.inf)

  for i in range(len(reader.color_files)):
    logging.info(f'i:{i}')
    color = reader.get_color(i)
    depth = reader.get_depth(i)
    if i==0:
      mask = reader.get_mask(0).astype(bool)
      pose = est.register(K=reader.K, rgb=color, depth=depth, ob_mask=mask, iteration=est_refine_iter)

    #   if debug>=3:
    #     m = mesh.copy()
    #     m.apply_transform(pose)
    #     m.export(f'{debug_dir}/model_tf.obj')
    #     xyz_map = depth2xyzmap(depth, reader.K)
    #     valid = depth>=0.001
    #     pcd = toOpen3dCloud(xyz_map[valid], color[valid])
    #     o3d.io.write_point_cloud(f'{debug_dir}/scene_complete.ply', pcd)
    else:
      pose = est.track_one(rgb=color, depth=depth, K=reader.K, iteration=track_refine_iter)

    os.makedirs(f'{debug_dir}/ob_in_cam', exist_ok=True)
    np.savetxt(f'{debug_dir}/ob_in_cam/{reader.id_strs[i]}.txt', pose.reshape(4,4))

    center_pose = pose@np.linalg.inv(to_origin)
    vis = draw_posed_3d_box(reader.K, img=color, ob_in_cam=center_pose, bbox=bbox)
    vis = draw_xyz_axis(color, ob_in_cam=center_pose, scale=0.1, K=reader.K, thickness=3, transparency=0, is_input_rgb=True)

    os.makedirs(f'{debug_dir}/track_vis', exist_ok=True)
    imageio.imwrite(f'{debug_dir}/track_vis/{reader.id_strs[i]}.png', vis)



class DataRequest(BaseModel):
    """
    Base-64 encoded string whose contents are a ZIP archive of the `/data` folder.
    """
    payload: str


class TransformResponse(BaseModel):
    """
    Server reply – a 4 × 4 homogeneous transform.
    """
    transform: List[List[float]]  # shape (4, 4)


def _dummy_estimate(data_dir: str) -> np.ndarray:
    """
    Replace this stub with a real call into the FoundationPose pipeline.

    Right now it just returns an identity matrix so that the end-to-end
    request/response flow works out of the box.
    """
    return np.eye(4, dtype=float)


@app.post("/estimate", response_model=TransformResponse)
async def estimate(data: DataRequest) -> TransformResponse:
    """
    1. Decode the base-64 payload back into raw ZIP bytes.
    2. Un-zip the dataset into a temporary directory (RAM /tmp).
    3. Run the pose-estimation routine.
    4. Return the 4 × 4 transform.
    """
    # Decode base-64 → raw bytes
    zip_bytes = base64.b64decode(data.payload)

    # Persist the dataset under /server_data (creates if missing)
    data_root = "server_data"
    os.makedirs(data_root, exist_ok=True)

    # Optionally, clear previous contents to avoid mixing datasets
    for root, dirs, files in os.walk(data_root):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(data_root)
        logging.info("Dataset received and extracted to %s", data_root)

    transform_mat = _compute_pose(data_root)

    return TransformResponse(transform=transform_mat.tolist())