using UnityEngine;
using System.Collections.Generic;
using System.Text;

public class SyntheticDatasetGenerator : MonoBehaviour
{
    [System.Serializable]
    public class ObjectDetails
    {
        public string name;
        public GeometryData3D geometry3D;
        public GeometryData2D geometry2D;
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
        public Vector2[] projectedCorners; // 2D screen positions of corners (mirrored y-coordinates)
    }

    [Tooltip("Main camera used for projecting 3D points to 2D")]
    public Camera mainCamera; // Main camera to project 3D points to 2D

    [Tooltip("List of all detected objects and their details")]
    public List<ObjectDetails> allObjectDetails;

    void Start()
    {
        if (mainCamera == null)
        {
            mainCamera = Camera.main; // Automatically use the main camera if not assigned
        }
        ExtractAndStoreObjectDetails();
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
                        projectedCorners = ProjectCorners(box.corners) // Project corners to 2D
                    }
                };

                allObjectDetails.Add(details);
            }
        }

        // Log the projected 2D corners as (x, mirrored y) tuples
        foreach (var detail in allObjectDetails)
        {
            Debug.Log("Object: " + detail.name);
            StringBuilder cornersOutput = new StringBuilder("Projected Corners: ");
            foreach (Vector2 corner in detail.geometry2D.projectedCorners)
            {
                cornersOutput.AppendFormat("({0:0}, {1:0}), ", corner.x, corner.y);
            }
            // Trim the trailing comma and space
            if (cornersOutput.Length > 0)
                cornersOutput.Remove(cornersOutput.Length - 2, 2);

            Debug.Log(cornersOutput.ToString());
        }
    }

    // Project 3D corner points to 2D screen space and mirror the y-coordinates
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
}
