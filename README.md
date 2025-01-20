# Master Thesis: Creating Immersive 3D Environments from Video

As computational power and device capabilities have advanced, Virtual Reality (VR) devices have grown in popularity, enabling realistic graphics and advanced recognition algorithms for scene analysis and user behavior understanding. VR is widely used across industries like automotive, entertainment, and education, with a notable application in employee training, where it optimizes time and costs by reducing staff expenses and training duration. However, creating detailed virtual environments remains resource-intensive, requiring precise measurements, multiple site visits, and manual 3D modeling when objects are unavailable. 

Together with AtlasVR and ICVR Lab this Master Thesis aims to optimize the process by developing methods for object detection and 6D pose estimation, creating an object library, dataset and synthetic dataset generation pipeline as well as designing a training framework to enable efficient reconstruction of virtual environments from real-world scenes. We introduce You Only Record Once (YORO), a network designed to estimate 6D Pose Estimation of the objects and room dimensions from a single video. Furthermore we also introduce the pipeline using 2 YORO instances to combine the informations coming from multiple camera viewframes.

<img width="655" alt="real2digital" src="https://github.com/user-attachments/assets/8694d940-5474-48d8-9d46-af30c233e12d" />

## Versions of the frameworks
we are using using python version 3.10.14 and Unity Editor version 2022.3.22f1.

## Python Packages
- PyTorch
- Numpy
- OpenCV
- Pillow
- Matplotlib
- Ultralytics
- Pandas
- Mpl-tool
- Scipy

## Repository Structure
Root Directory
- Dataset Manager/
- lifting_models/
- Pipeline/
- runs/
- yolo/

### YOLOv8
Under yolo directory:
- **yolo_train** for finetuning model, config.yaml file should be configured
- **yolo_analysis** jupyter notebooks file to measure the accuracy
- **yolo_inference** to use the yolo on one image
  
runs/pose includes the finetuned weights.

### SYE Model
Under lifting_models directory:
- **sye** jupyter notebooks file to train, test and measure the accuracy
- **sye_inference** to use it standalone as well as in different pipelines

### YORO Model and Pipeline
Under pipeline
- **yolo_sye** 2-staged pipeline to perform pose estimation and 2D-3D Lifting to predict 6D Pose from single monocular image.
- **yoro_pipeline** The final pipeline which is capable of handling 2 Camera Inputs using 2 YORO instances.
  
### Dataset Generation
We are using Unity to generate synthetic dataset to be used to train our models. This includes annotated synthetic images for finetuning YOLOv8 and 2D-3D Data to train 2D-3D Lifting model.

Unity Project is in Dataset Manager directory, which also includes dataset_validator to validate the generated synthetic data.

Inside the project in Dataset Generator Scene, Controller GameObject has RoomGenerator and SyntheticDatasetGenerator Scripts attached. The Object references should be filled out with room dimensions and min/max objects to spawn.

Furthermore one needs to define the DatasetName and number of images as well as number of test images to be generated.

Upon playing and pressing "G" Dataset Generation Loop will start. Furthermore one can also generate and destroy one room by pressing "P" and "O" 

## Assets Used in the Unity Project

- **[Voxel Office Props](https://assetstore.unity.com/packages/3d/props/voxel-office-props-127772):**  
  A set of voxel-style office furniture and props, used for generating synthetic rooms.

- **[Sketchfab for Unity](https://assetstore.unity.com/packages/tools/input-management/sketchfab-for-unity-14302):**  
  A tool that integrates Sketchfab’s 3D model library directly into Unity, used for importing Sketchfab models.

- **[Free Wood Door Pack](https://assetstore.unity.com/packages/3d/props/interior/free-wood-door-pack-280509):**  
  A collection of wooden door models, used for generating synthetic rooms.

- **[50 Free PBR Materials](https://assetstore.unity.com/packages/2d/textures-materials/50-free-pbr-materials-242760):**  
  A versatile set of free Physically Based Rendering (PBR) materials for texturing walls, floors, and other surfaces.

- **[Chair and Sofa Set](https://assetstore.unity.com/packages/3d/props/furniture/chair-and-sofa-set-263004):**  
  A detailed set of chair and sofa models, used for generating synthetic rooms.

- **[Stylized Guns Pack](https://assetstore.unity.com/packages/3d/props/stylized-guns-pack-233145):**  
  A pack of stylized gun models, hologram material is used for placing predicted rooms by our pipeline.







