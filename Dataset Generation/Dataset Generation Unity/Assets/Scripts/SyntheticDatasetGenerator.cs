using UnityEngine;
using System.IO;
using System.Collections.Generic;
using System.Text;
using System.Collections;

public class SyntheticDatasetGenerator : MonoBehaviour
{
    [System.Serializable]
    public class ObjectDetails
    {
        public string name;
        public GeometryData3D geometry3D;
        public GeometryData2D geometry2D;              // Non-normalized 2D data
        public GeometryData2D geometry2DNormalized;    // Normalized 2D data
    }

    [System.Serializable]
    public class GeometryData3D
    {
        public Vector3 position;
        public Vector3 rotation;
        public Vector3[] corners; // 3D world positions of corners

        public Vector3 relativePosition;
        public Vector3 relativeRotation;
        public Vector3[] relativeCorners; // 3D world positions of corners relative to camera
    }

    [System.Serializable]
    public class GeometryData2D
    {
        public Vector2 boundingBoxCenter;  // Center of the bounding box
        public Vector2 boundingBoxSize;    // Size of the bounding box (width, height)
        public Vector2[] projectedCorners; // 2D screen positions of corners
    }

    [Tooltip("Main camera used for projecting 3D points to 2D")]
    public Camera mainCamera;

    [Tooltip("Name of the Dataset to be created")]
    public string dataSetName;

    [Tooltip("Buffer to add to the bounding box size (in pixels)")]
    public float boundingBoxBuffer;

    [Tooltip("Toggle for capturing a screenshot or not")]
    public bool takeScreenshot = true;

    [Tooltip("Number of base images to generate (excluding test)")]
    public int numberOfImages;

    [Tooltip("Number of iiterations, after which a new room would be generated")]
    public int iterationForRoom;

    [Tooltip("Delay between captures in seconds")]
    public float delayBetweenCaptures;

    [Tooltip("Screen width for capturing screenshots")]
    public int screenWidth;

    [Tooltip("Screen height for capturing screenshots")]
    public int screenHeight;

    [Tooltip("Track iteration for file naming")]
    public int pictureIndex = 0;

    [Tooltip("Fixed n images go to 'test'")]
    public int testThreshold;

    [Tooltip("List of all detected objects and their details")]
    public List<ObjectDetails> allObjectDetails;

    private RoomGenerator roomGenerator; // Reference to RoomGenerator script
    private SceneReconstructor sceneReconstructor; // Reference to SceneReconstructor script
    private string baseDirectory = @"C:\Users\sakar\OneDrive\mt-datas\synthetic_data\";
    private string debugDirectory = @"C:\Users\sakar\OneDrive\mt-datas\synth_validation_data\";
    private string dataSetDirectory = "";
    private int trainThreshold; // Threshold for images going to the 'train' set
    private int valThreshold; // Threshold for images going to the 'val' set
    private int totalImagesToGenerate; // Total number of images including test set

    private GameObject GeneratedRoom; // Reference to the GeneratedRoom created by RoomGenerator

    // Map object names/tags to IDs (Chair -> 0, Desk -> 1, Wall -> 2)
    int MapObjectNameToID(string name)
    {
        if (name.Contains("Vertex")) return 0;
        else if (name.Contains("Cabinet")) return 1;
        else if (name.Contains("Common Chair")) return 2;
        else if (name.Contains("Desk")) return 3;
        else if (name.Contains("Door")) return 4;
        else if (name.Contains("Laptop")) return 5;
        else if (name.Contains("Monitor")) return 6;
        else if (name.Contains("Office Chair")) return 7;
        else if (name.Contains("Pendant")) return 8;
        else if (name.Contains("Robotic Arm")) return 9;
        else if (name.Contains("Sofa")) return 10;
        else if (name.Contains("Window")) return 11;
        else return -1;  // Default for unrecognized objects
    }

    void Start()
    {
        roomGenerator = GetComponent<RoomGenerator>();
        sceneReconstructor = GetComponent<SceneReconstructor>();

        dataSetDirectory = Path.Combine(baseDirectory, dataSetName);

        if (mainCamera == null)
        {
            mainCamera = Camera.main; // Automatically use the main camera if not assigned
        }

        screenWidth = Screen.width;
        screenHeight = Screen.height;

        // Calculate how many images go into train, val, and test sets
        totalImagesToGenerate = numberOfImages + testThreshold; // Add extra 5 for test
        trainThreshold = Mathf.FloorToInt(0.8f * numberOfImages);
        valThreshold = numberOfImages - trainThreshold; // Remaining images go to 'val'

        // Ensure necessary directories exist
        CreateNecessaryDirectories();

        SaveCameraIntrinsicMatrix();
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.G))
        {
            StartCoroutine(GenerateDataPoints());
        }
        if (Input.GetKeyDown(KeyCode.L))
        {
            GenerateOneDataPoint();
        }
    }

    void CreateNecessaryDirectories()
    {
        // Ensure the main directories and subdirectories (train, val, test) exist
        string[] subFolders = { "train", "val", "test" };

        foreach (var folder in subFolders)
        {
            Directory.CreateDirectory(Path.Combine(dataSetDirectory, "images", folder));
            Directory.CreateDirectory(Path.Combine(dataSetDirectory, "labels", folder));
        }

        Directory.CreateDirectory(Path.Combine(dataSetDirectory, "2d_data"));
        Directory.CreateDirectory(Path.Combine(dataSetDirectory, "3d_data"));
        Directory.CreateDirectory(Path.Combine(dataSetDirectory, "scene_meta"));
    }

    void SaveCameraIntrinsicMatrix()
    {
        // Calculate intrinsic parameters
        float width = mainCamera.pixelWidth;
        float height = mainCamera.pixelHeight;
        float fx = (width / 2.0f) / Mathf.Tan(mainCamera.fieldOfView * 0.5f * Mathf.Deg2Rad);
        float fy = (height / 2.0f) / Mathf.Tan(mainCamera.fieldOfView * 0.5f * Mathf.Deg2Rad);
        float cx = width / 2.0f;
        float cy = height / 2.0f;

        // Construct the intrinsic matrix as a string for easy saving
        StringBuilder intrinsicMatrixBuilder = new StringBuilder();
        intrinsicMatrixBuilder.AppendLine("Intrinsic Matrix:");
        intrinsicMatrixBuilder.AppendLine($"{fx} 0 {cx} 0");
        intrinsicMatrixBuilder.AppendLine($"0 {fy} {cy} 0");
        intrinsicMatrixBuilder.AppendLine($"0 0 1 0");
        intrinsicMatrixBuilder.AppendLine($"0 0 0 1");

        // Save to a file
        string intrinsicFilePath = Path.Combine(dataSetDirectory, "camera_intrinsic_matrix.txt");
        File.WriteAllText(intrinsicFilePath, intrinsicMatrixBuilder.ToString());

        Debug.Log($"Intrinsic matrix saved to: {intrinsicFilePath}");
    }

    void GenerateOneDataPoint()
    {
        // Extract object details for the current image
        ExtractAndStoreObjectDetails();

        // Serialize the 3D and normalized 2D data for each image
        SerializeAllGeometryData3DToCSV(Path.Combine(debugDirectory, dataSetName, $"{dataSetName}_{sceneReconstructor.fileNumber}_3d.csv"));
        SerializeAllGeometryData2DNormalizedToCSV(Path.Combine(debugDirectory, dataSetName, $"{dataSetName}_{sceneReconstructor.fileNumber}_2d.csv"));

        // Serialize normalized 2D data to COCO-style TXT
        SerializeGeometryData2DNormalizedToTXT(Path.Combine(debugDirectory, dataSetName, $"{dataSetName}_{sceneReconstructor.fileNumber}_coco.txt"));

        // Serialize the transform data of the GeneratedRoom and save as CSV
        SerializeTransformsToCSV(Path.Combine(debugDirectory, dataSetName, $"{dataSetName}_{sceneReconstructor.fileNumber}_meta.csv"));

        // Capture screenshot
        if (takeScreenshot)
        {
            CaptureScreenshotAndSave(Path.Combine(debugDirectory, dataSetName, $"{dataSetName}_{sceneReconstructor.fileNumber}_pic.png"));
        }
    }

    IEnumerator GenerateDataPoints()
    {
        // Every x iterations, generate a new room
        if (pictureIndex % iterationForRoom == 0)
        {
            roomGenerator.DeleteRoom();
            yield return new WaitForSeconds(0.2f);
            roomGenerator.GenerateRoom();
            roomGenerator.SetupCameraPositions();
        }

        else
        {
            roomGenerator.MoveToNextCameraPosition();
        }

        yield return new WaitForSeconds(0.2f);
        // Move the camera to the next position on each iteration

        GeneratedRoom = GameObject.Find("GeneratedRoom"); // Reference the newly generated room

        // Determine which set (train, val, test) this image should go into
        string dataSplit = GetDataSplit();

        // Extract object details for the current image
        ExtractAndStoreObjectDetails();

        // Serialize the 3D and normalized 2D data for each image
        SerializeAllGeometryData3DToCSV(Path.Combine(dataSetDirectory, "3d_data", $"{pictureIndex}.csv"));
        SerializeAllGeometryData2DNormalizedToCSV(Path.Combine(dataSetDirectory, "2d_data", $"{pictureIndex}.csv"));

        // Serialize normalized 2D data to COCO-style TXT
        SerializeGeometryData2DNormalizedToTXT(Path.Combine(dataSetDirectory, "labels", dataSplit, $"{pictureIndex}.txt"));

        // Serialize the transform data of the GeneratedRoom and save as CSV
        SerializeTransformsToCSV(Path.Combine(dataSetDirectory, "scene_meta", $"{pictureIndex}.csv"));

        // Capture screenshot
        if (takeScreenshot)
        {
            CaptureScreenshotAndSave(Path.Combine(dataSetDirectory, "images", dataSplit, $"{pictureIndex}.png"));
        }

        // Increment picture index for the next iteration
        pictureIndex++;

        // If there are more images to generate, continue after a delay
        if (pictureIndex < totalImagesToGenerate)
        {
            yield return new WaitForSeconds(delayBetweenCaptures); // Wait for the specified delay
            StartCoroutine(GenerateDataPoints()); // Recursively call the function
        }
        else
        {
            Debug.Log("All images and data generation completed.");
        }
    }

    string GetDataSplit()
    {
        if (pictureIndex < trainThreshold)
        {
            return "train";
        }
        else if (pictureIndex < trainThreshold + valThreshold)
        {
            return "val";
        }
        else
        {
            return "test";
        }
    }

    void ExtractAndStoreObjectDetails()
    {
        GameObject[] taggedObjects = GameObject.FindGameObjectsWithTag("Detect");
        allObjectDetails = new List<ObjectDetails>();

        foreach (GameObject obj in taggedObjects)
        {
            BoundingBoxHandler box = obj.GetComponent<BoundingBoxHandler>();
            if (box != null) // Ensure there is a BoundingBox component
            {
                Vector2[] projectedCorners = ProjectCorners(box.corners);

                // Get visibility status for each corner
                int[] visibility = CheckCornersVisibility(projectedCorners);

                // Check if at least 8 corners are visible (i.e., have a visibility status of 2)
                int visibleCount = 0;
                foreach (int vis in visibility)
                {
                    if (vis == 2) visibleCount++; // Updated check for visibility status to 2
                }

                // If fewer than 8 corners are visible, skip the object
                if (visibleCount < 8)
                {
                    Debug.Log($"Object '{obj.name}' does not have at least 8 visible corners. Skipping.");
                    continue;
                }

                // Calculate non-normalized bounding box
                Vector2 center, size;
                CalculateBoundingBox(projectedCorners, out center, out size, false);

                // Normalize the corners and bounding box
                Vector2[] normalizedCorners = NormalizeCorners(projectedCorners);
                Vector2 normalizedCenter, normalizedSize;
                CalculateBoundingBox(normalizedCorners, out normalizedCenter, out normalizedSize, true);

                ObjectDetails details = new ObjectDetails
                {
                    name = obj.name,
                    geometry3D = new GeometryData3D
                    {
                        position = obj.transform.position,
                        rotation = obj.transform.eulerAngles,
                        corners = box.corners
                    },
                    geometry2D = new GeometryData2D
                    {
                        projectedCorners = projectedCorners,
                        boundingBoxCenter = center,
                        boundingBoxSize = size
                    },
                    geometry2DNormalized = new GeometryData2D
                    {
                        projectedCorners = normalizedCorners,
                        boundingBoxCenter = normalizedCenter,
                        boundingBoxSize = normalizedSize
                    }
                };

                // Calculate relative transformations and store them
                CalculateRelativeTransformations(details, obj.transform);

                allObjectDetails.Add(details);
            }
        }

        Debug.Log("Extracted " + allObjectDetails.Count + " objects with at least 8 visible corners.");
    }

    // Method to calculate relative position and rotation
    void CalculateRelativeTransformations(ObjectDetails details, Transform objTransform)
    {
        // Calculate relative position
        Vector3 objectPosition = objTransform.position;
        Vector3 cameraPosition = mainCamera.transform.position;
        Quaternion cameraRotation = mainCamera.transform.rotation;

        // Transform the object's global position to the camera's local space
        details.geometry3D.relativePosition = Quaternion.Inverse(cameraRotation) * (objectPosition - cameraPosition);

        // Calculate relative rotation
        Quaternion objectRotation = objTransform.rotation;
        Quaternion relativeRotation = Quaternion.Inverse(cameraRotation) * objectRotation;

        // Convert relative rotation to Euler angles (Vector3)
        details.geometry3D.relativeRotation = relativeRotation.eulerAngles;

        // Calculate relative corner positions
        details.geometry3D.relativeCorners = new Vector3[details.geometry3D.corners.Length];
        for (int i = 0; i < details.geometry3D.corners.Length; i++)
        {
            Vector3 cornerGlobalPosition = details.geometry3D.corners[i];
            Vector3 cornerRelativePosition = cornerGlobalPosition - cameraPosition;
            details.geometry3D.relativeCorners[i] = Quaternion.Inverse(cameraRotation) * cornerRelativePosition;
        }
    }



    int[] CheckCornersVisibility(Vector2[] projectedCorners)
    {
        int[] visibility = new int[projectedCorners.Length]; // Array to store visibility (2 for visible, 1 for invisible)

        for (int i = 0; i < projectedCorners.Length; i++)
        {
            Vector2 corner = projectedCorners[i];
            if (corner.x >= 0 && corner.x <= screenWidth && corner.y >= 0 && corner.y <= screenHeight)
            {
                visibility[i] = 2; // Corner is visible (updated to 2)
            }
            else
            {
                visibility[i] = 1; // Corner is outside the screen (invisible, remains 1)
            }
        }

        return visibility;
    }


    // Method to calculate bounding box based on 2D corners and apply the buffer
    void CalculateBoundingBox(Vector2[] corners, out Vector2 center, out Vector2 size, bool isNormalized)
    {
        float minX = float.MaxValue;
        float maxX = float.MinValue;
        float minY = float.MaxValue;
        float maxY = float.MinValue;

        // Calculate the min and max x and y values
        foreach (Vector2 corner in corners)
        {
            if (corner.x < minX) minX = corner.x;
            if (corner.x > maxX) maxX = corner.x;
            if (corner.y < minY) minY = corner.y;
            if (corner.y > maxY) maxY = corner.y;
        }

        // Adjust buffer size based on whether the data is normalized or not
        float buffer = isNormalized ? boundingBoxBuffer / screenWidth : boundingBoxBuffer;

        // Calculate center and size of the bounding box
        center = new Vector2((minX + maxX) / 2, (minY + maxY) / 2);
        size = new Vector2((maxX - minX) + buffer * 2, (maxY - minY) + buffer * 2);
    }

    // Method to project 3D corner points to 2D screen space and mirror the y-coordinates
    Vector2[] ProjectCorners(Vector3[] corners)
    {
        Vector2[] projectedCorners = new Vector2[corners.Length];
        for (int i = 0; i < corners.Length; i++)
        {
            Vector3 screenPoint = mainCamera.WorldToScreenPoint(corners[i]);
            // Mirror the y-coordinate by subtracting it from the screen height
            projectedCorners[i] = new Vector2(screenPoint.x, screenHeight - screenPoint.y);
        }
        return projectedCorners;
    }

    // Normalize the 2D corners based on the screen width and height set from the editor
    Vector2[] NormalizeCorners(Vector2[] corners)
    {
        Vector2[] normalizedCorners = new Vector2[corners.Length];
        for (int i = 0; i < corners.Length; i++)
        {
            normalizedCorners[i] = new Vector2(corners[i].x / screenWidth, corners[i].y / screenHeight);
        }
        return normalizedCorners;
    }

    // Serialize the transform components (position, rotation, and scale) of all child objects in GeneratedRoom
    void SerializeTransformsToCSV(string filePath)
    {
        List<string> transformData = new List<string>();

        // Ensure GeneratedRoom is available
        if (GeneratedRoom != null)
        {
            // Get all children of the GeneratedRoom GameObject
            foreach (Transform child in GeneratedRoom.transform)
            {
                string data = SerializeTransform(child);
                transformData.Add(data);
            }

            // Also serialize the main camera's transform
            if (mainCamera != null)
            {
                string cameraData = SerializeTransform(mainCamera.transform);
                transformData.Add(cameraData);
            }

            // Write the data to the CSV file
            File.WriteAllLines(filePath, transformData);
            Debug.Log($"Scene metadata (transforms) saved to: {filePath}");
        }
        else
        {
            Debug.LogError("GeneratedRoom is not available for serialization.");
        }
    }

    // Method to serialize transform data into a CSV format string
    string SerializeTransform(Transform objTransform)
    {
        Vector3 position = objTransform.position; // Global position
        Vector3 rotation = objTransform.rotation.eulerAngles; // Global rotation in Euler angles
        Vector3 scale = objTransform.lossyScale; // Global scale

        // Format as CSV (name, position, rotation, scale)
        return $"{objTransform.name},{position.x},{position.y},{position.z}," +
               $"{rotation.x},{rotation.y},{rotation.z}," +
               $"{scale.x},{scale.y},{scale.z}";
    }

    // Serialize all GeometryData3D for all objects into a CSV file
    void SerializeAllGeometryData3DToCSV(string filePath)
    {
        StringBuilder csvBuilder = new StringBuilder();

        foreach (var details in allObjectDetails)
        {
            int objectID = MapObjectNameToID(details.name); // Map object name to ID
            StringBuilder rowBuilder = new StringBuilder();
            rowBuilder.Append($"{objectID},");

            // Append relative position and rotation
            rowBuilder.Append($"{details.geometry3D.relativePosition.x},{details.geometry3D.relativePosition.y},{details.geometry3D.relativePosition.z},");
            rowBuilder.Append($"{details.geometry3D.relativeRotation.x},{details.geometry3D.relativeRotation.y},{details.geometry3D.relativeRotation.z},");

            // Append relative corners
            foreach (var corner in details.geometry3D.relativeCorners)
            {
                rowBuilder.Append($"{corner.x},{corner.y},{corner.z},");
            }

            csvBuilder.AppendLine(rowBuilder.ToString().TrimEnd(',')); // Trim the last comma
        }

        File.WriteAllText(filePath, csvBuilder.ToString());
        Debug.Log($"Relative 3D data for all objects saved to: {filePath}");
    }


    // Serialize all normalized GeometryData2D for all objects into a CSV file
    void SerializeAllGeometryData2DNormalizedToCSV(string filePath)
    {
        StringBuilder csvBuilder = new StringBuilder();

        foreach (var details in allObjectDetails)
        {
            int objectID = MapObjectNameToID(details.name); // Map object name to ID
            StringBuilder rowBuilder = new StringBuilder();
            rowBuilder.Append($"{objectID},");

            // Append bounding box center and size (normalized)
            rowBuilder.Append($"{details.geometry2DNormalized.boundingBoxCenter.x},{details.geometry2DNormalized.boundingBoxCenter.y},");
            rowBuilder.Append($"{details.geometry2DNormalized.boundingBoxSize.x},{details.geometry2DNormalized.boundingBoxSize.y},");

            // Append normalized 2D corners (X, Y for each corner)
            foreach (var corner in details.geometry2DNormalized.projectedCorners)
            {
                rowBuilder.Append($"{corner.x},{corner.y},");
            }

            csvBuilder.AppendLine(rowBuilder.ToString().TrimEnd(',')); // Trim the last comma
        }

        File.WriteAllText(filePath, csvBuilder.ToString());
        Debug.Log($"Normalized 2D data for all objects saved to: {filePath}");
    }

    // Serialize GeometryData2DNormalized to a COCO-like TXT file (without headers, spaces between values)
    void SerializeGeometryData2DNormalizedToTXT(string filePath)
    {
        StringBuilder txtBuilder = new StringBuilder();

        foreach (var details in allObjectDetails)
        {
            // Get the object ID based on its name
            int objectID = MapObjectNameToID(details.name);

            // Add bounding box center and size, separated by spaces
            string boundingBoxCenter = $"{details.geometry2DNormalized.boundingBoxCenter.x:F4} {details.geometry2DNormalized.boundingBoxCenter.y:F4}";
            string boundingBoxSize = $"{details.geometry2DNormalized.boundingBoxSize.x:F4} {details.geometry2DNormalized.boundingBoxSize.y:F4}";

            // Get the visibility status of each corner
            int[] cornerVisibility = CheckCornersVisibility(details.geometry2DNormalized.projectedCorners);

            // Flatten the keypoints (x, y pairs with visibility flags)
            List<string> keypointsWithVisibility = new List<string>();
            for (int i = 0; i < details.geometry2DNormalized.projectedCorners.Length; i++)
            {
                Vector2 corner = details.geometry2DNormalized.projectedCorners[i];
                keypointsWithVisibility.Add($"{corner.x:F4} {corner.y:F4} {cornerVisibility[i]}"); // Add x, y and visibility (1 or 2)
            }

            // Construct the line with space-separated values (use the object ID instead of name)
            txtBuilder.AppendLine($"{objectID} {boundingBoxCenter} {boundingBoxSize} {string.Join(" ", keypointsWithVisibility)}");
        }

        // Write to the TXT file
        File.WriteAllText(filePath, txtBuilder.ToString());
        Debug.Log($"GeometryData2DNormalized TXT saved to: {filePath}");
    }

    // Capture screenshot using Unity's built-in ScreenCapture function
    void CaptureScreenshotAndSave(string filePath)
    {
        ScreenCapture.CaptureScreenshot(filePath);
        Debug.Log($"Screenshot saved to: {filePath}");
    }
}
