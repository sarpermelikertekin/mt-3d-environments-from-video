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
    }

    [System.Serializable]
    public class GeometryData2D
    {
        public Vector2 boundingBoxCenter;  // Center of the bounding box
        public Vector2 boundingBoxSize;    // Size of the bounding box (width, height)
        public Vector2[] projectedCorners; // 2D screen positions of corners
    }

    [Tooltip("Main camera used for projecting 3D points to 2D")]
    public Camera mainCamera; // Main camera to project 3D points to 2D

    [Tooltip("Buffer to add to the bounding box size (in pixels)")]
    public float boundingBoxBuffer = 25f; // Buffer for the bounding box

    [Tooltip("Toggle for capturing a screenshot or not")]
    public bool takeScreenshot = true; // Whether or not to capture screenshots

    [Tooltip("Number of base images to generate (excluding test)")]
    public int numberOfImages = 10; // Number of base images to generate (80% train, 20% val)

    [Tooltip("Delay between captures in seconds")]
    public float delayBetweenCaptures = 1f; // Time delay between each iteration

    [Tooltip("Screen width for capturing screenshots")]
    public int screenWidth;

    [Tooltip("Screen height for capturing screenshots")]
    public int screenHeight;

    [Tooltip("List of all detected objects and their details")]
    public List<ObjectDetails> allObjectDetails;

    private RoomGenerator roomGenerator; // Reference to RoomGenerator script
    private string baseDirectory = @"C:\Users\sakar\OneDrive\mt-datas\synthetic_data\0_test\";
    private int pictureIndex = 0; // Track iteration for file naming
    private int trainThreshold; // Threshold for images going to the 'train' set
    private int valThreshold; // Threshold for images going to the 'val' set
    private int testThreshold = 5; // Fixed 5 images go to 'test'
    private int totalImagesToGenerate; // Total number of images including test set

    void Start()
    {
        roomGenerator = GetComponent<RoomGenerator>();

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

        // Start the recursive image generation process
        StartCoroutine(GenerateImageWithDelay());
    }

    void CreateNecessaryDirectories()
    {
        // Ensure the main directories and subdirectories (train, val, test) exist
        string[] subFolders = { "train", "val", "test" };

        foreach (var folder in subFolders)
        {
            Directory.CreateDirectory(Path.Combine(baseDirectory, "images", folder));
            Directory.CreateDirectory(Path.Combine(baseDirectory, "labels", folder));
            Directory.CreateDirectory(Path.Combine(baseDirectory, "2d_data", folder));
            Directory.CreateDirectory(Path.Combine(baseDirectory, "3d_data", folder));
        }
    }

    IEnumerator GenerateImageWithDelay()
    {
        // Every 20 iterations, generate a new room
        if (pictureIndex % 20 == 0)
        {
            roomGenerator.GenerateRoom();
            roomGenerator.SetupCameraPositions();
        }

        // Move the camera to the next position on each iteration
        roomGenerator.MoveToNextCameraPosition();

        // Determine which set (train, val, test) this image should go into
        string dataSplit = GetDataSplit();

        // Extract object details for the current image
        ExtractAndStoreObjectDetails();

        // Serialize the 3D and normalized 2D data for each image
        SerializeAllGeometryData3DToCSV(dataSplit);
        SerializeAllGeometryData2DNormalizedToCSV(dataSplit);

        // Serialize normalized 2D data to COCO-style TXT
        SerializeGeometryData2DNormalizedToTXT(dataSplit);

        // Capture screenshot
        if (takeScreenshot)
        {
            CaptureScreenshotAndSave(dataSplit);
        }

        // Increment picture index for the next iteration
        pictureIndex++;

        // If there are more images to generate, continue after a delay
        if (pictureIndex < totalImagesToGenerate)
        {
            yield return new WaitForSeconds(delayBetweenCaptures); // Wait for the specified delay
            StartCoroutine(GenerateImageWithDelay()); // Recursively call the function
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
            BoundingBox box = obj.GetComponent<BoundingBox>();
            if (box != null) // Ensure there is a BoundingBox component
            {
                Vector2[] projectedCorners = ProjectCorners(box.corners);

                // Check if the object is fully visible in the game tab
                if (!AreCornersInView(projectedCorners))
                {
                    Debug.Log($"Object '{obj.name}' is not fully visible in the game view. Skipping.");
                    continue; // Skip objects that aren't fully visible
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

                allObjectDetails.Add(details);
            }
        }

        Debug.Log("Extracted " + allObjectDetails.Count + " fully visible object details.");
    }

    // Check if all corners are within the screen bounds
    bool AreCornersInView(Vector2[] projectedCorners)
    {
        foreach (Vector2 corner in projectedCorners)
        {
            if (corner.x < 0 || corner.x > screenWidth || corner.y < 0 || corner.y > screenHeight)
            {
                return false; // If any corner is out of bounds, the object is not fully visible
            }
        }
        return true; // All corners are within the screen bounds
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
            Debug.Log(corners[i]);
            normalizedCorners[i] = new Vector2(corners[i].x / screenWidth, corners[i].y / screenHeight);
            Debug.Log(normalizedCorners[i]);
        }
        return normalizedCorners;
    }

    // Map object names/tags to IDs (Chair -> 0, Desk -> 1, Wall -> 2)
    int MapObjectNameToID(string name)
    {
        if (name.Contains("Chair")) return 0;
        else if (name.Contains("Desk")) return 1;
        else if (name.Contains("Wall")) return 2;
        else return -1;  // Default for unrecognized objects
    }

    // Serialize all GeometryData3D for all objects into a CSV file
    void SerializeAllGeometryData3DToCSV(string dataSplit)
    {
        StringBuilder csvBuilder = new StringBuilder();
        csvBuilder.AppendLine("objectID,objectName,positionX,positionY,positionZ,rotationX,rotationY,rotationZ,corner1X,corner1Y,corner1Z,corner2X,corner2Y,corner2Z,...");

        foreach (var details in allObjectDetails)
        {
            int objectID = MapObjectNameToID(details.name); // Map object name to ID
            StringBuilder rowBuilder = new StringBuilder();
            rowBuilder.Append($"{objectID},{details.name},");
            rowBuilder.Append($"{details.geometry3D.position.x},{details.geometry3D.position.y},{details.geometry3D.position.z},");
            rowBuilder.Append($"{details.geometry3D.rotation.x},{details.geometry3D.rotation.y},{details.geometry3D.rotation.z},");

            // Append corners (X, Y, Z for each corner)
            foreach (var corner in details.geometry3D.corners)
            {
                rowBuilder.Append($"{corner.x},{corner.y},{corner.z},");
            }

            csvBuilder.AppendLine(rowBuilder.ToString().TrimEnd(',')); // Trim the last comma
        }

        string filePath = Path.Combine(baseDirectory, "3d_data", dataSplit, $"{pictureIndex}.csv");

        File.WriteAllText(filePath, csvBuilder.ToString());
        Debug.Log($"3D data for all objects saved to: {filePath}");
    }

    // Serialize all normalized GeometryData2D for all objects into a CSV file
    void SerializeAllGeometryData2DNormalizedToCSV(string dataSplit)
    {
        StringBuilder csvBuilder = new StringBuilder();
        csvBuilder.AppendLine("objectID,objectName,corner1X,corner1Y,corner2X,corner2Y,corner3X,corner3Y,...,boundingBoxCenterX,boundingBoxCenterY,boundingBoxWidth,boundingBoxHeight");

        foreach (var details in allObjectDetails)
        {
            int objectID = MapObjectNameToID(details.name); // Map object name to ID
            StringBuilder rowBuilder = new StringBuilder();
            rowBuilder.Append($"{objectID},{details.name},");

            // Append bounding box center and size (normalized)
            rowBuilder.Append($"{details.geometry2DNormalized.boundingBoxCenter.x},{details.geometry2DNormalized.boundingBoxCenter.y},");
            rowBuilder.Append($"{details.geometry2DNormalized.boundingBoxSize.x},{details.geometry2DNormalized.boundingBoxSize.y}");

            // Append normalized 2D corners (X, Y for each corner)
            foreach (var corner in details.geometry2DNormalized.projectedCorners)
            {
                rowBuilder.Append($"{corner.x},{corner.y},");
            }

            csvBuilder.AppendLine(rowBuilder.ToString().TrimEnd(',')); // Trim the last comma
        }

        string filePath = Path.Combine(baseDirectory, "2d_data", dataSplit, $"{pictureIndex}.csv");

        File.WriteAllText(filePath, csvBuilder.ToString());
        Debug.Log($"Normalized 2D data for all objects saved to: {filePath}");
    }

    // Serialize GeometryData2DNormalized to a COCO-like TXT file (without headers, tabs between values)
    void SerializeGeometryData2DNormalizedToTXT(string dataSplit)
    {
        StringBuilder txtBuilder = new StringBuilder();

        foreach (var details in allObjectDetails)
        {
            // Get the object ID based on its name
            int objectID = MapObjectNameToID(details.name);

            // Add bounding box center and size, separated by tabs
            string boundingBoxCenter = $"{details.geometry2DNormalized.boundingBoxCenter.x:F4} {details.geometry2DNormalized.boundingBoxCenter.y:F4}";
            string boundingBoxSize = $"{details.geometry2DNormalized.boundingBoxSize.x:F4} {details.geometry2DNormalized.boundingBoxSize.y:F4}";

            // Flatten the keypoints (x, y pairs)
            List<string> keypoints = new List<string>();
            foreach (var corner in details.geometry2DNormalized.projectedCorners)
            {
                keypoints.Add($"{corner.x:F4} {corner.y:F4}"); // Add the normalized coordinates with precision and spaces between x and y
            }

            // Construct the line with tab-separated values (use the object ID instead of name)
            txtBuilder.AppendLine($"{objectID} {boundingBoxCenter} {boundingBoxSize} {string.Join(" ", keypoints)}");
        }

        string filePath = Path.Combine(baseDirectory, "labels", dataSplit, $"{pictureIndex}.txt");

        File.WriteAllText(filePath, txtBuilder.ToString());
        Debug.Log($"GeometryData2DNormalized TXT saved to: {filePath}");
    }

    // Capture screenshot using Unity's built-in ScreenCapture function
    void CaptureScreenshotAndSave(string dataSplit)
    {
        string screenshotFilePath = Path.Combine(baseDirectory, "images", dataSplit, $"{pictureIndex}.png");
        ScreenCapture.CaptureScreenshot(screenshotFilePath);
        Debug.Log($"Screenshot saved to: {screenshotFilePath}");
    }
}
