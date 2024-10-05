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

    void Start()
    {
        if (mainCamera == null)
        {
            mainCamera = Camera.main; // Automatically use the main camera if not assigned
        }

        // Extract object details and log them to console
        ExtractAndStoreObjectDetails();
        Log2DDataToConsole();

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

    // Log the 2D data (both normalized and non-normalized) in a readable format to the console
    void Log2DDataToConsole()
    {
        foreach (var detail in allObjectDetails)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine($"Object: {detail.name}");

            // Log non-normalized corners
            sb.AppendLine("Projected 2D Corners (x, y):");
            foreach (Vector2 corner in detail.geometry2D.projectedCorners)
            {
                sb.AppendLine($"({corner.x:F2}, {corner.y:F2})");
            }

            // Log normalized corners
            sb.AppendLine("Normalized 2D Corners (x, y):");
            foreach (Vector2 corner in detail.geometry2DNormalized.projectedCorners)
            {
                sb.AppendLine($"({corner.x:F2}, {corner.y:F2})");
            }

            // Log non-normalized bounding box
            sb.AppendLine($"Bounding Box Center: ({detail.geometry2D.boundingBoxCenter.x:F2}, {detail.geometry2D.boundingBoxCenter.y:F2})");
            sb.AppendLine($"Bounding Box Size: Width = {detail.geometry2D.boundingBoxSize.x:F2}, Height = {detail.geometry2D.boundingBoxSize.y:F2}");

            // Log normalized bounding box
            sb.AppendLine($"Normalized Bounding Box Center: ({detail.geometry2DNormalized.boundingBoxCenter.x:F2}, {detail.geometry2DNormalized.boundingBoxCenter.y:F2})");
            sb.AppendLine($"Normalized Bounding Box Size: Width = {detail.geometry2DNormalized.boundingBoxSize.x:F2}, Height = {detail.geometry2DNormalized.boundingBoxSize.y:F2}");

            sb.AppendLine(new string('-', 50));

            // Log the string to the console
            Debug.Log(sb.ToString());
        }
    }

    // Separate function to capture the screenshot using the CaptureScreenshot class
    void CaptureScreenshotAndSave()
    {
        if (CaptureScreenshot.Instance != null)
        {
            CaptureScreenshot.Instance.capture = true; // Ensure capture is enabled
            string screenshotFilePath = @"C:\Users\sakar\OneDrive\mt-datas\synthetic_data\0_test\";

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
