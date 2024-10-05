using UnityEngine;
using System.IO;
using System.Collections.Generic;
using System.Text;

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
        public Vector2[] projectedCorners; // 2D screen positions of corners
        public Vector2 boundingBoxCenter; // Center of the bounding box
        public Vector2 boundingBoxSize; // Size of the bounding box (width, height)
    }

    [Tooltip("Main camera used for projecting 3D points to 2D")]
    public Camera mainCamera; // Main camera to project 3D points to 2D

    [Tooltip("List of all detected objects and their details")]
    public List<ObjectDetails> allObjectDetails;

    [Tooltip("Buffer to add to the bounding box size (in pixels)")]
    public float boundingBoxBuffer = 25f; // Buffer for the bounding box

    private string baseDirectory = @"C:\Users\sakar\OneDrive\mt-datas\synthetic_data\0_test\";

    void Start()
    {
        if (mainCamera == null)
        {
            mainCamera = Camera.main; // Automatically use the main camera if not assigned
        }

        // Extract object details
        ExtractAndStoreObjectDetails();

        // Serialize 3D and non-normalized 2D to JSON and normalized 2D to CSV
        foreach (var details in allObjectDetails)
        {
            SerializeGeometryData3D(details);
            SerializeGeometryData2D(details);
        }

        SerializeGeometryData2DNormalizedToCSV();  // COCO-style CSV for normalized 2D data

        // Capture the screenshot
        CaptureScreenshotAndSave();
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

        Debug.Log("Extracted " + allObjectDetails.Count + " object details.");
    }

    // Method to calculate bounding box based on 2D corners and apply the buffer
    // `isNormalized` determines whether the bounding box is normalized or not
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
        float buffer = isNormalized ? boundingBoxBuffer / Screen.width : boundingBoxBuffer;

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
            projectedCorners[i] = new Vector2(screenPoint.x, Screen.height - screenPoint.y);
        }
        return projectedCorners;
    }

    // Normalize the 2D corners based on screen width and height
    Vector2[] NormalizeCorners(Vector2[] corners)
    {
        Vector2[] normalizedCorners = new Vector2[corners.Length];
        for (int i = 0; i < corners.Length; i++)
        {
            normalizedCorners[i] = new Vector2(corners[i].x / Screen.width, corners[i].y / Screen.height);
        }
        return normalizedCorners;
    }

    // Serialize GeometryData3D to JSON
    void SerializeGeometryData3D(ObjectDetails details)
    {
        string json3D = JsonUtility.ToJson(details.geometry3D, true);
        string filePath = Path.Combine(baseDirectory, $"{details.name}_Geometry3D.json");

        File.WriteAllText(filePath, json3D);
        Debug.Log($"GeometryData3D for {details.name} saved to: {filePath}");
    }

    // Serialize GeometryData2D (non-normalized) to JSON
    void SerializeGeometryData2D(ObjectDetails details)
    {
        string json2D = JsonUtility.ToJson(details.geometry2D, true);
        string filePath = Path.Combine(baseDirectory, $"{details.name}_Geometry2D.json");

        File.WriteAllText(filePath, json2D);
        Debug.Log($"GeometryData2D for {details.name} saved to: {filePath}");
    }

    // Serialize GeometryData2DNormalized to a COCO-like CSV file
    void SerializeGeometryData2DNormalizedToCSV()
    {
        StringBuilder csv = new StringBuilder();
        csv.AppendLine("id,keypoints,bounding_box_center,bounding_box_size");

        foreach (var details in allObjectDetails)
        {
            // Generate the object ID
            string id = details.name;

            // Flatten the keypoints (x, y pairs)
            List<string> keypoints = new List<string>();
            foreach (var corner in details.geometry2DNormalized.projectedCorners)
            {
                keypoints.Add($"{corner.x:F4},{corner.y:F4}"); // Add the normalized coordinates with precision
            }

            // Add bounding box center and size
            string boundingBoxCenter = $"{details.geometry2DNormalized.boundingBoxCenter.x:F4},{details.geometry2DNormalized.boundingBoxCenter.y:F4}";
            string boundingBoxSize = $"{details.geometry2DNormalized.boundingBoxSize.x:F4},{details.geometry2DNormalized.boundingBoxSize.y:F4}";

            // Construct the CSV line
            csv.AppendLine($"{id},{string.Join(",", keypoints)},{boundingBoxCenter},{boundingBoxSize}");
        }

        string filePath = Path.Combine(baseDirectory, "Geometry2DNormalized_COCO.csv");

        File.WriteAllText(filePath, csv.ToString());
        Debug.Log($"GeometryData2DNormalized CSV saved to: {filePath}");
    }

    // Separate function to capture the screenshot using the CaptureScreenshot class
    void CaptureScreenshotAndSave()
    {
        if (CaptureScreenshot.Instance != null)
        {
            CaptureScreenshot.Instance.capture = true; // Ensure capture is enabled
            string screenshotFilePath = baseDirectory;

            // Ensure the directory exists; if not, create it
            if (!Directory.Exists(screenshotFilePath))
            {
                Directory.CreateDirectory(screenshotFilePath);
                Debug.Log("Directory created at: " + screenshotFilePath);
            }

            // Capture the screenshot
            CaptureScreenshot.Instance.TakeScreenshot(screenshotFilePath);
            Debug.Log("Screenshot saved to: " + screenshotFilePath);

            // Increment picture index for the next screenshot
            CaptureScreenshot.Instance.pictureIndex++;
        }
    }
}
